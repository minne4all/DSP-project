from flask import Flask, render_template, request, redirect, flash, send_file, url_for, jsonify
import os
import requests
import rdflib
from pyshacl import validate
import re
import json
import zipfile
import rdflib

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuration Shacl
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

GRAPHDB_BASE_URL = "http://localhost:7200"
REPOSITORY_NAME = "nen2660-poc"
SPARQL_UPDATE_ENDPOINT = f"{GRAPHDB_BASE_URL}/repositories/{REPOSITORY_NAME}/statements"
SHAPES_FILE_PATH = "shapes/shacl-shapes.ttl"

#Configuration for the AERIUS API
UPLOAD_FOLDER = "outputs"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

CALCULATION_BASE_URL = "https://connect.aerius.nl/api/v8/own2000/calculate"
JOB_BASE_URL = "https://connect.aerius.nl/api/v8/jobs"

API_KEY = "acca4ef0301a4f019b7a6bc99e6781d4"
jobs = {}

# Load templates
with open('./template gml/featurecollection.gml', 'r') as file:
    featcoll = file.read()

with open('./template gml/mobile source.gml', 'r') as file:
    moso = file.read()

with open('./template gml/specmobsource.gml', 'r') as file:
    specmob = file.read()

with open('./template gml/calcpoint.gml', 'r') as file:
    calcpoint = file.read()


# Function to for shacl validation
def sparql_update(update_query):
    """Send SPARQL update queries to the GraphDB repository."""
    headers = {"Content-Type": "application/sparql-update"}
    response = requests.post(SPARQL_UPDATE_ENDPOINT, data=update_query, headers=headers)
    response.raise_for_status()

def construct_insert_query(graph_uri, rdf_data):
    """
    Construct a SPARQL INSERT query, extracting @prefix lines
    from the Turtle data and converting them to PREFIX statements.
    """
    prefix_pattern = r"@prefix\s+([\w\-]+):\s+<([^>]+)>\s*\."
    prefixes = re.findall(prefix_pattern, rdf_data)
    prefix_statements = "\n".join([f"PREFIX {pfx}: <{uri}>" for pfx, uri in prefixes])

    # Remove the @prefix lines from the original RDF data
    rdf_data_no_prefix = re.sub(prefix_pattern, "", rdf_data)

    return f"""
    {prefix_statements}

    INSERT DATA {{
      GRAPH <{graph_uri}> {{
        {rdf_data_no_prefix}
      }}
    }}
    """

def validate_and_extract_constraints(data_graph):
    """
    Helper function that:
      - Validates data_graph against the SHAPES_FILE_PATH
      - Returns: (conforms, shacl_constraint_list, grouped_messages, error_details, violations_count)
    """
    # Parse the shapes graph
    shapes_graph = rdflib.Graph()
    shapes_graph.parse(SHAPES_FILE_PATH, format="turtle")

    # Validate
    c, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        inference="rdfs"
    )

    # Build result
    conforms = c
    shacl_constraint = []
    grouped_messages = {}
    error_details = None
    violations_count = 0

    if not conforms:
        # Collect all results
        all_results = list(results_graph.subjects(
            rdflib.RDF.type,
            rdflib.URIRef("http://www.w3.org/ns/shacl#ValidationResult")
        ))
        violations_count = len(all_results)
        error_details = results_text

        # Build the 'shacl_constraint' list
        for result in all_results:
            focus_node = results_graph.value(
                subject=result,
                predicate=rdflib.URIRef("http://www.w3.org/ns/shacl#focusNode")
            )
            result_path = results_graph.value(
                subject=result,
                predicate=rdflib.URIRef("http://www.w3.org/ns/shacl#resultPath")
            )
            severity = results_graph.value(
                subject=result,
                predicate=rdflib.URIRef("http://www.w3.org/ns/shacl#resultSeverity")
            )
            source_shape = results_graph.value(
                subject=result,
                predicate=rdflib.URIRef("http://www.w3.org/ns/shacl#sourceShape")
            )
            message = results_graph.value(
                subject=result,
                predicate=rdflib.URIRef("http://www.w3.org/ns/shacl#resultMessage")
            )
            min_count = results_graph.value(
                subject=result,
                predicate=rdflib.URIRef("http://www.w3.org/ns/shacl#minCount")
            )

            violation = {
                "focus_node": str(focus_node) if focus_node else None,
                "result_path": str(result_path) if result_path else None,
                "severity": str(severity) if severity else None,
                "source_shape": str(source_shape) if source_shape else None,
                "message": str(message) if message else None,
                "min_count": str(min_count) if min_count else None,
            }
            shacl_constraint.append(violation)

        # Group by message so each message is shown once
        for v in shacl_constraint:
            msg = v["message"]
            if msg not in grouped_messages:
                grouped_messages[msg] = []
            grouped_messages[msg].append(v)

    return (conforms, shacl_constraint, grouped_messages, error_details, violations_count)


#Functions for AERIUS API
def fill_template(template, **kwargs):
    return template.format(**kwargs)


def start_calculation(filepath):
    options = {
        "name": "Nitrogen Deposition Calculation",
        "calculationYear": 2025,
        "sendEmail": False,
        "outputType": "PDF",
        "calculationPointsType": "OWN2000_RECEPTORS",
    }
    files = [
        {
            "fileName": os.path.basename(filepath),
            "situation": "ALL",
            "groupId": 1,
            "substance": "NH3",
            "calculationYear": 2025,
            "nettingFactor": None,
        }
    ]
    headers = {
        "api-key": API_KEY,
        "Accept": "application/json",
    }
    data = {
        "options": json.dumps(options),
        "files": json.dumps(files),
    }
    file_uploads = [("fileParts", open(filepath, "rb"))]
    
    response = requests.post(CALCULATION_BASE_URL, headers=headers, data=data, files=file_uploads)
    if response.status_code == 200:
        result = response.json()
        if result.get("successful"):
            return result["jobKey"]
    return None

def retrieve_job_result(job_key):
    headers = {
        "api-key": API_KEY,
        "Accept": "application/json",
    }
    response = requests.get(f"{JOB_BASE_URL}/{job_key}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

def extract_mobile_sources_from_ontology(g):
    mobile_sources = []
    
    for source in g.subjects(rdflib.RDF.type, rdflib.URIRef("http://example.org/graphs/aerius-extension#MobileSource")):
        mosolabel = g.value(source, rdflib.URIRef("http://example.org/graphs/aerius-extension#mosolabel"))
        mosoposition = g.value(source, rdflib.URIRef("http://example.org/graphs/aerius-extension#mosoposition"))
        sectorid = g.value(source, rdflib.URIRef("http://example.org/graphs/aerius-extension#sectorid"))
        emissions = {
            "NH3": g.value(source, rdflib.URIRef("http://example.org/graphs/aerius-extension#emitsNH3")),
            "NOX": g.value(source, rdflib.URIRef("http://example.org/graphs/aerius-extension#emitsNOX")),
            "PM10": g.value(source, rdflib.URIRef("http://example.org/graphs/aerius-extension#emitsPM10")),
            "NO2": g.value(source, rdflib.URIRef("http://example.org/graphs/aerius-extension#emitsNO2"))
        }

        # Extract specific mobile sources
        specific_sources = []
        for specific in g.objects(source, rdflib.URIRef("http://example.org/graphs/aerius-extension#hasSpecificMobileSource")):
            mobtype = g.value(specific, rdflib.URIRef("http://example.org/graphs/aerius-extension#mobtype"))
            fuelyear = g.value(specific, rdflib.URIRef("http://example.org/graphs/aerius-extension#fuelyear"))
            description = g.value(specific, rdflib.URIRef("http://example.org/graphs/aerius-extension#description"))
            specific_sources.append({"mobtype": mobtype, "fuelyear": fuelyear, "description": description})

        mobile_sources.append({
            "label": mosolabel,
            "position": mosoposition,
            "sectorid": sectorid,
            "emissions": emissions,
            "specific_sources": specific_sources
        })

    return mobile_sources

def generate_gml_from_ontology(g):
    mobile_sources = extract_mobile_sources_from_ontology(g)
    featuremembers = ''.join(mobile_sources) + calcpoint

    metadata = {
        "name": "Generated from Ontology",
        "year": "2025",
        "featuremembers": featuremembers
    }

    gml_content = fill_template(featcoll, **metadata)
    return gml_content

def generate_gml_from_form_data(form_data):
    mobile_sources = []

    for source in form_data["mobile_sources"]:
        specmosos = ''.join([
            fill_template(specmob, **specific)
            for specific in source["specific_sources"]
        ])

        mosodata = {
            "label": source["label"],
            "position": source["position"],
            "sectorid": source["sectorid"],
            **source["emissions"],
            "specficimobilesource": specmosos,
            "q": "1"
        }
        mobile_sources.append(fill_template(moso, **mosodata))

    featuremembers = ''.join(mobile_sources) + calcpoint
    metadata = {"name": form_data["name"], "year": form_data["year"], "featuremembers": featuremembers}

    return fill_template(featcoll, **metadata)

#App routes for Shacl
@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main route:
      - GET: show the page with uploaded files
      - POST:
        1) Upload a new .ttl file
        2) Or if user selects a file and clicks "Process Selected File", re-validate that file
    """
    uploaded_files = os.listdir(app.config["UPLOAD_FOLDER"])

    # Template vars
    success = None
    error = None
    error_details = None
    shacl_constraint = []
    file_data = []
    conforms = True
    violations_count = 0
    grouped_messages = {}

    # 1) User is uploading a new file
    if request.method == "POST" and "nen_file" in request.files:
        file = request.files["nen_file"]
        if not file.filename.endswith(".ttl"):
            error = "Please upload a valid Turtle (.ttl) file."
        else:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    rdf_data = f.read()

                data_graph = rdflib.Graph()
                data_graph.parse(data=rdf_data, format="turtle")

                # For display
                file_data = [
                    {"subject": str(s), "predicate": str(p), "object": str(o)}
                    for s, p, o in data_graph
                ]

                # Validate with pySHACL
                c, sc, gm, ed, vc = validate_and_extract_constraints(data_graph)
                conforms = c
                shacl_constraint = sc
                grouped_messages = gm
                error_details = ed
                violations_count = vc

                if not conforms:
                    error = "Your file failed SHACL validation."
                else:
                    # Insert into GraphDB if it passes
                    graph_uri = f"http://example.org/graphs/{file.filename}"
                    insert_query = construct_insert_query(graph_uri, rdf_data)
                    sparql_update(insert_query)
                    success = (
                        f"File '{file.filename}' validated and uploaded to GraphDB "
                        f"as <{graph_uri}>."
                    )

            except Exception as e:
                error = f"Error uploading file '{file.filename}': {str(e)}"

    # 2) User selected an existing file to re-validate
    elif request.method == "POST" and "selected_file" in request.form:
        selected_file = request.form.get("selected_file")
        if selected_file:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], selected_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        rdf_data = f.read()

                    data_graph = rdflib.Graph()
                    data_graph.parse(data=rdf_data, format="turtle")

                    # For display
                    file_data = [
                        {"subject": str(s), "predicate": str(p), "object": str(o)}
                        for s, p, o in data_graph
                    ]

                    # Validate existing data
                    c, sc, gm, ed, vc = validate_and_extract_constraints(data_graph)
                    conforms = c
                    shacl_constraint = sc
                    grouped_messages = gm
                    error_details = ed
                    violations_count = vc

                    if not conforms:
                        error = f"File '{selected_file}' failed SHACL validation."
                    else:
                        success = (
                            f"File '{selected_file}' re-validated successfully. "
                            "No SHACL violations found."
                        )
                except Exception as e:
                    error = f"Error processing file '{selected_file}': {str(e)}"
            else:
                error = f"File '{selected_file}' does not exist."
        else:
            error = "No file selected to process."

    return render_template(
        "index.html",
        uploaded_files=uploaded_files,
        success=success,
        error=error,
        error_details=error_details,
        shacl_constraint=shacl_constraint,
        file_data=file_data,
        conforms=conforms,
        violations_count=violations_count,
        grouped_messages=grouped_messages
    )

@app.route("/delete-file", methods=["POST"])
def delete_file():
    """Delete file route (loads a confirmation page)."""
    file_name = request.form.get("file_name")
    if not file_name:
        return render_template(
            "index.html",
            error="No file specified for deletion.",
            uploaded_files=os.listdir(app.config["UPLOAD_FOLDER"]),
            shacl_constraint=[],
            file_data=[],
            conforms=True,
            violations_count=0,
            grouped_messages={}
        )
    return render_template(
        "confirm_delete.html",
        file_name=file_name,
        uploaded_files=os.listdir(app.config["UPLOAD_FOLDER"]),
        shacl_constraint=[],
        file_data=[],
        conforms=True,
        violations_count=0,
        grouped_messages={}
    )

@app.route("/delete-confirmed", methods=["POST"])
def delete_confirmed():
    """Performs the actual file+graph deletion."""
    file_name = request.form.get("file_name")
    if not file_name:
        return render_template(
            "index.html",
            error="No file specified for deletion.",
            uploaded_files=os.listdir(app.config["UPLOAD_FOLDER"]),
            shacl_constraint=[],
            file_data=[],
            conforms=True,
            violations_count=0,
            grouped_messages={}
        )

    try:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        graph_uri = f"http://example.org/graphs/{file_name}"
        delete_query = f"DROP GRAPH <{graph_uri}>"
        sparql_update(delete_query)

        success = f"File '{file_name}' and its data in GraphDB have been deleted."
        return render_template(
            "index.html",
            success=success,
            uploaded_files=os.listdir(app.config["UPLOAD_FOLDER"]),
            shacl_constraint=[],
            file_data=[],
            conforms=True,
            violations_count=0,
            grouped_messages={}
        )
    except Exception as e:
        error = f"Error deleting file '{file_name}': {str(e)}"
        return render_template(
            "index.html",
            error=error,
            uploaded_files=os.listdir(app.config["UPLOAD_FOLDER"]),
            shacl_constraint=[],
            file_data=[],
            conforms=True,
            violations_count=0,
            grouped_messages={}
        )

@app.route("/shacl-summary", methods=["GET"])
def shacl_summary():
    """
    Parse and return a human-readable summary of SHACL constraints as JSON.
    If you want it as an HTML page, you can convert the JSON response into
    a template or transform it in client-side code.
    """
    if not os.path.exists(SHAPES_FILE_PATH):
        return jsonify({"error": "SHACL shapes file not found."}), 404

    try:
        g = rdflib.Graph()
        g.parse(SHAPES_FILE_PATH, format="turtle")

        constraints = []
        for shape in g.subjects(rdflib.RDF.type, rdflib.URIRef("http://www.w3.org/ns/shacl#NodeShape")):
            shape_name = g.value(shape, rdflib.RDFS.label) or shape
            properties = []

            for prop in g.objects(shape, rdflib.URIRef("http://www.w3.org/ns/shacl#property")):
                path = g.value(prop, rdflib.URIRef("http://www.w3.org/ns/shacl#path"))
                min_count = g.value(prop, rdflib.URIRef("http://www.w3.org/ns/shacl#minCount"))
                max_count = g.value(prop, rdflib.URIRef("http://www.w3.org/ns/shacl#maxCount"))
                message = g.value(prop, rdflib.URIRef("http://www.w3.org/ns/shacl#message"))

                properties.append({
                    "path": str(path) if path else None,
                    "min_count": str(min_count) if min_count else None,
                    "max_count": str(max_count) if max_count else None,
                    "message": str(message) if message else None
                })

            constraints.append({
                "shape": str(shape_name),
                "properties": properties
            })

        return jsonify(constraints)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update-triples", methods=["POST"])
def update_triples():
    """
    Receives JSON payload:
      {
        "filename": "someFile.ttl",
        "triples": [
          {"subject": "...", "predicate": "...", "object": "..."},
          ...
        ]
      }
    Appends these triple(s) to the named file, re-runs SHACL validation,
    and returns JSON with 'conforms' plus violation info or errors.
    """
    try:
        data = request.get_json()
        filename = data.get('filename')
        triple_updates = data.get('triples', [])

        if not filename:
            return jsonify({"error": "No filename provided."}), 400

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if not os.path.exists(file_path):
            return jsonify({"error": f"File '{filename}' not found."}), 400

        # Parse existing graph
        g = rdflib.Graph()
        g.parse(file_path, format="turtle")

        # Add the new/updated triples
        for t in triple_updates:
            subj_str = t.get('subject', '').strip()
            pred_str = t.get('predicate', '').strip()
            obj_str  = t.get('object', '').strip()
            if subj_str and pred_str and obj_str:
                s = rdflib.URIRef(subj_str)  # or interpret if it's not a URI
                p = rdflib.URIRef(pred_str)
                # For a simple approach, treat object as literal:
                o = rdflib.Literal(obj_str, datatype=rdflib.XSD.string)
                g.add((s, p, o))

        # Overwrite the file with updated data
        g.serialize(destination=file_path, format="turtle")

        # Re-validate
        shapes_graph = rdflib.Graph()
        shapes_graph.parse(SHAPES_FILE_PATH, format="turtle")
        conforms, results_graph, results_text = validate(
            g,
            shacl_graph=shapes_graph,
            data_graph_format="turtle",
            shacl_graph_format="turtle",
            inference="rdfs"
        )

        if not conforms:
            all_results = list(results_graph.subjects(
                rdflib.RDF.type,
                rdflib.URIRef("http://www.w3.org/ns/shacl#ValidationResult")
            ))
            return jsonify({
                "conforms": False,
                "violations_count": len(all_results),
                "report": results_text
            })
        else:
            return jsonify({
                "conforms": True,
                "report": results_text
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# "./ontology/aerius-extension2.ttl"
#App routes for AERIUS API
@app.route('/aerius', methods=['GET', 'POST'])
def aerius():
    ontology_path = "./ontology/aerius-extension2.ttl"
    g = rdflib.Graph()
    g.parse(ontology_path, format="turtle")

    # Extract all available projects
    projects = []
    for project in g.subjects(rdflib.RDF.type, rdflib.URIRef("http://example.org/graphs/aerius-extension#ConstructionProject")):
        label = g.value(project, rdflib.RDFS.label)
        projects.append({"uri": str(project), "label": str(label)})

    form_data = {
        "name": "",
        "year": "2025",
        "mobile_sources": []
    }

    selected_project = request.args.get("project")
    if selected_project:
        # Load details for the selected project
        project_uri = rdflib.URIRef(selected_project)
        form_data["name"] = g.value(project_uri, rdflib.RDFS.label, default="Unnamed Project")

        # Extract associated activities
        activities = g.objects(project_uri, rdflib.URIRef("http://example.org/graphs/aerius-extension#includes"))
        for activity in activities:
            mobile_source = g.value(activity, rdflib.URIRef("http://example.org/graphs/aerius-extension#hasEmissionSource"))
            if mobile_source:
                specific_sources = []
                for specific in g.objects(mobile_source, rdflib.URIRef("http://example.org/graphs/aerius-extension#hasSpecificMobileSource")):
                    specific_sources.append({
                        "mobtype": g.value(specific, rdflib.URIRef("http://example.org/graphs/aerius-extension#mobtype")),
                        "fuelyear": g.value(specific, rdflib.URIRef("http://example.org/graphs/aerius-extension#fuelyear")),
                        "description": g.value(specific, rdflib.URIRef("http://example.org/graphs/aerius-extension#description"))
                    })

                form_data["mobile_sources"].append({
                    "label": g.value(mobile_source, rdflib.URIRef("http://example.org/graphs/aerius-extension#mosolabel")),
                    "position": g.value(mobile_source, rdflib.URIRef("http://example.org/graphs/aerius-extension#mosoposition")),
                    "sectorid": g.value(mobile_source, rdflib.URIRef("http://example.org/graphs/aerius-extension#sectorid")),
                    "emissions": {
                        "NH3": g.value(mobile_source, rdflib.URIRef("http://example.org/graphs/aerius-extension#emitsNH3")),
                        "NOX": g.value(mobile_source, rdflib.URIRef("http://example.org/graphs/aerius-extension#emitsNOX")),
                        "PM10": g.value(mobile_source, rdflib.URIRef("http://example.org/graphs/aerius-extension#emitsPM10")),
                        "NO2": g.value(mobile_source, rdflib.URIRef("http://example.org/graphs/aerius-extension#emitsNO2"))
                    },
                    "specific_sources": specific_sources
                })

    if request.method == 'POST':
        # Get updated data from the form
        form_data["name"] = request.form.get("name", "Default Project Name")
        form_data["year"] = request.form.get("year", "2025")

        # Update mobile sources with user-edited values
        updated_mobile_sources = []
        for i, source in enumerate(form_data["mobile_sources"]):
            updated_source = {
                "label": request.form.get(f"mosolabel_{i}", source["label"]),
                "position": request.form.get(f"mosoposition_{i}", source["position"]),
                "sectorid": request.form.get(f"sectorid_{i}", source["sectorid"]),
                "emissions": {
                    "NH3": request.form.get(f"NH3_{i}", source["emissions"]["NH3"]),
                    "NOX": request.form.get(f"NOX_{i}", source["emissions"]["NOX"]),
                    "PM10": request.form.get(f"PM10_{i}", source["emissions"]["PM10"]),
                    "NO2": request.form.get(f"NO2_{i}", source["emissions"]["NO2"]),
                },
                "specific_sources": []
            }

            # Handle specific mobile sources
            for j, specific in enumerate(source["specific_sources"]):
                updated_specific = {
                    "mobtype": request.form.get(f"mobtype_{i}_{j}", specific["mobtype"]),
                    "fuelyear": request.form.get(f"fuelyear_{i}_{j}", specific["fuelyear"]),
                    "description": request.form.get(f"description_{i}_{j}", specific["description"]),
                    "fueloruse": 'operatingHoursPerYear' if specific["mobtype"] in ['B2T', 'B4T', 'LPG'] else 'literFuelPerYear'
                }
                updated_source["specific_sources"].append(updated_specific)

            updated_mobile_sources.append(updated_source)

        form_data["mobile_sources"] = updated_mobile_sources

        # Generate GML content
        gml_content = generate_gml_from_form_data(form_data)

        # Save GML file
        output_path = os.path.join(UPLOAD_FOLDER, 'output.gml')
        with open(output_path, 'w') as file:
            file.write(gml_content)

        # Start calculation
        job_key = start_calculation(output_path)
        if job_key:
            jobs[job_key] = {"status": "running", "files": []}
            flash("Calculation started. Job key added to status section.")
        else:
            flash("Failed to start the calculation.")

        return redirect(url_for('aerius'))

    return render_template('combined_ui.html', projects=projects, selected_project=selected_project, form_data=form_data, jobs=jobs)




@app.route('/aerius/check_status/<job_key>', methods=['GET'])
def check_status(job_key):
    job_info = retrieve_job_result(job_key)
    if job_info:
        if job_info.get("status") == "COMPLETED":
            result_url = job_info.get("resultUrl")
            if result_url:
                zip_path = os.path.join(RESULT_FOLDER, f"{job_key}.zip")
                response = requests.get(result_url)
                with open(zip_path, "wb") as zip_file:
                    zip_file.write(response.content)
                
                extract_to = os.path.join(RESULT_FOLDER, job_key)
                os.makedirs(extract_to, exist_ok=True)
                extract_zip(zip_path, extract_to)
                
                pdf_files = [f for f in os.listdir(extract_to) if f.endswith('.pdf')]
                jobs[job_key] = {"status": "completed", "files": pdf_files, "folder": job_key}
        else:
            jobs[job_key]["status"] = job_info.get("status", "unknown")
    return redirect(url_for('aerius'))


@app.route('/aerius/view/<folder>/<filename>')
def view_file(folder, filename):
    pdf_path = os.path.join(RESULT_FOLDER, folder, filename)
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=False)
    flash("File not found.")
    return redirect('/aerius')


@app.route('/aerius/download/<folder>/<filename>')
def download_file(folder, filename):
    pdf_path = os.path.join(RESULT_FOLDER, folder, filename)
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    flash("File not found.")
    return redirect('/aerius')

if __name__ == "__main__":
    app.run(debug=True)
