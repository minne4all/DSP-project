from flask import Flask, render_template, request, jsonify
import os
import requests
import rdflib
from pyshacl import validate
import re

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

GRAPHDB_BASE_URL = "http://localhost:7200"
REPOSITORY_NAME = "nen2660-poc"
SPARQL_UPDATE_ENDPOINT = f"{GRAPHDB_BASE_URL}/repositories/{REPOSITORY_NAME}/statements"
SHAPES_FILE_PATH = "shapes/shacl-shapes.ttl"

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

if __name__ == "__main__":
    app.run(debug=True)
