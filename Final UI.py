from flask import Flask, render_template, request, redirect, flash, send_file, url_for, jsonify
import os
import requests
import rdflib
from pyshacl import validate
import re
import json
import zipfile
import rdflib
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuration Shacl
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

GRAPHDB_BASE_URL = "http://localhost:7200"
REPOSITORY_NAME = "DSP"
SPARQL_UPDATE_ENDPOINT = f"{GRAPHDB_BASE_URL}/repositories/{REPOSITORY_NAME}/statements"
SHAPES_FILE_PATH = "shapes/new-shapes.ttl"

# Store newly added triples in memory (the “New Document”).
added_triples_history = []
# Last validated data’s triple set (for display).
LAST_UPLOADED_FILE_JSON = "last_uploaded_file.json"
# SHACL shape overview & violations for the index page.
SHACL_OVERVIEW_JSON = "shacl_overview.json"

#Configuration for the AERIUS API
UPLOAD_FOLDER = "gml outputs"
RESULT_FOLDER = "aerius results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

CALCULATION_BASE_URL = "https://connect.aerius.nl/api/v8/own2000/calculate"
JOB_BASE_URL = "https://connect.aerius.nl/api/v8/jobs"

API_KEY = "acca4ef0301a4f019b7a6bc99e6781d4"
jobs = {}

# Load templates
with open('./gml templates/featurecollection.gml', 'r') as file:
    featcoll = file.read()

with open('./gml templates/mobile source.gml', 'r') as file:
    moso = file.read()

with open('./gml templates/specmobsource.gml', 'r') as file:
    specmob = file.read()

with open('./gml templates/calcpoint.gml', 'r') as file:
    calcpoint = file.read()


# Function to for shacl validation
def parse_numeric(num_str):
    """
    Returns e.g. '"123"^^xsd:decimal' if it’s numeric,
    else falls back to plain string.
    """
    try:
        float_val = float(num_str)
        # If it has a decimal point, store as decimal else integer
        if '.' in num_str:
            return f'"{num_str}"^^xsd:decimal'
        else:
            return f'"{num_str}"^^xsd:integer'
    except:
        # fallback
        return f'"{num_str}"'

def parse_numeric_or_uri(obj_str):
    """
    If obj_str starts with http => treat as URIRef
    else parse as numeric if possible, else string
    """
    if obj_str.startswith("http://") or obj_str.startswith("https://"):
        return f'<{obj_str}>'
    return parse_numeric(obj_str)

def sparql_update(update_query: str) -> None:
    """
    Send a SPARQL UPDATE query to GraphDB.
    """
    headers = {"Content-Type": "application/sparql-update"}
    response = requests.post(SPARQL_UPDATE_ENDPOINT, data=update_query, headers=headers)
    response.raise_for_status()

def construct_insert_query(graph_uri: str, rdf_data: str) -> str:
    """
    Convert @prefix lines from Turtle into SPARQL PREFIX statements, then INSERT the rest.
    """
    prefix_pattern = r"@prefix\s+([\w\-]+):\s+<([^>]+)>\s*\."
    prefixes = re.findall(prefix_pattern, rdf_data)
    prefix_statements = "\n".join(f"PREFIX {p}: <{u}>" for p, u in prefixes)

    rdf_data_no_prefix = re.sub(prefix_pattern, "", rdf_data)
    return f"""
    {prefix_statements}
    INSERT DATA {{
      GRAPH <{graph_uri}> {{
        {rdf_data_no_prefix}
      }}
    }}
    """

def build_shape_overview(data_graph, shapes_graph, violations):
    """
    Build an overview of shapes and their conformance, used for the index page’s summary.
    """
    from collections import defaultdict
    from rdflib.namespace import RDF
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")

    shape2violations = defaultdict(list)
    for v in violations:
        shape2violations[v["source_shape"]].append(v)

    overview = []
    for shape_node in shapes_graph.subjects(RDF.type, SH.NodeShape):
        shape_name = str(shape_node)
        desc_val = shapes_graph.value(shape_node, SH.description)
        desc_str = str(desc_val) if desc_val else ""
        target_class = shapes_graph.value(shape_node, SH.targetClass)

        has_instance = False
        if target_class:
            has_instance = any(True for _ in data_graph.subjects(RDF.type, target_class))

        if has_instance:
            if shape_name in shape2violations:
                total_count = len(shape2violations[shape_name])
                if total_count > 0:
                    overview.append({
                        "shape_name": shape_name,
                        "shape_description": desc_str,
                        "status": "Violated",
                        "focus_nodes": list({v["focus_node"] for v in shape2violations[shape_name]}),
                        "progress": f"0% (still {total_count} violation(s))"
                    })
                else:
                    overview.append({
                        "shape_name": shape_name,
                        "shape_description": desc_str,
                        "status": "Conforms",
                        "focus_nodes": [],
                        "progress": "100% (all fixed!)"
                    })
            else:
                overview.append({
                    "shape_name": shape_name,
                    "shape_description": desc_str,
                    "status": "Conforms",
                    "focus_nodes": [],
                    "progress": "100%"
                })
        else:
            # No instance found in data OR shape has no targetClass
            if shape_name in shape2violations:
                f_nodes = list({v["focus_node"] for v in shape2violations[shape_name]})
                overview.append({
                    "shape_name": shape_name,
                    "shape_description": desc_str,
                    "status": "Violated",
                    "focus_nodes": f_nodes,
                    "progress": "0%"
                })
            else:
                # Not in data
                overview.append({
                    "shape_name": shape_name,
                    "shape_description": desc_str,
                    "status": "Not in data" if target_class else "Conforms or Not Applicable",
                    "focus_nodes": [],
                    "progress": "N/A" if target_class else "100%"
                })

    return overview

def lookup_shacl_datatype(shape_uri, property_uri):
    """
    Look up the property constraints in the shape graph, returning possible datatypes or an 'object' marker.
    """
    shapes_graph = rdflib.Graph()
    shapes_graph.parse(SHAPES_FILE_PATH, format="turtle")

    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    shape_node = rdflib.URIRef(shape_uri)
    property_node = None

    # Find the property shape that matches property_uri
    for prop_bnode in shapes_graph.objects(shape_node, SH.property):
        p = shapes_graph.value(prop_bnode, SH.path)
        if p and str(p) == property_uri:
            property_node = prop_bnode
            break

    if not property_node:
        return []

    # Check if there's sh:datatype or sh:or
    datatypes = []
    or_list = list(shapes_graph.objects(property_node, SH.or_))
    if or_list:
        # e.g. sh:or([ sh:datatype xsd:decimal ], [ sh:datatype xsd:integer ])
        for or_bnode in or_list:
            for item in shapes_graph.items(or_bnode):
                dt = shapes_graph.value(item, SH.datatype)
                if dt:
                    datatypes.append(str(dt))
    else:
        # No sh:or => check direct sh:datatype
        dt = shapes_graph.value(property_node, SH.datatype)
        if dt:
            datatypes.append(str(dt))

    # If none found => possibly an object property
    return datatypes

def _handle_violations(data_graph, shapes_graph, results_graph, results_text, error_msg):
    """
    Parse validation results, store them in JSON, then redirect with an error message if needed.
    """
    from rdflib.namespace import RDF
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")

    violations = []
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        focus_node = results_graph.value(result, SH.focusNode)
        result_path = results_graph.value(result, SH.resultPath)
        severity = results_graph.value(result, SH.resultSeverity)
        source_shape = results_graph.value(result, SH.sourceShape)
        message = results_graph.value(result, SH.resultMessage)
        min_count = results_graph.value(result, SH.minCount)

        if isinstance(source_shape, rdflib.BNode):
            parent_shapes = list(shapes_graph.subjects(predicate=SH.property, object=source_shape))
            if parent_shapes:
                source_shape = parent_shapes[0]

        violations.append({
            "focus_node": str(focus_node) if focus_node else None,
            "result_path": str(result_path) if result_path else None,
            "severity": str(severity) if severity else None,
            "source_shape": str(source_shape) if source_shape else None,
            "message": str(message) if message else None,
            "min_count": str(min_count) if min_count else None,
        })

    overview = build_shape_overview(data_graph, shapes_graph, violations)
    with open(SHACL_OVERVIEW_JSON, "w") as f:
        json.dump({"overview": overview, "violations": violations}, f, indent=2)

    merged_triples = [(str(s), str(p), str(o)) for (s, p, o) in data_graph]
    with open(LAST_UPLOADED_FILE_JSON, "w") as f:
        json.dump(merged_triples, f, indent=2)

    return redirect(url_for("index", error=error_msg, error_details=results_text))

def create_rdflib_node(value: str):
    """
    Naive approach: if it starts with http:// => URIRef, else treat as literal.
    (Could be enhanced to parse shape constraints for typed literals.)
    """
    if value.startswith("http://") or value.startswith("https://"):
        return rdflib.URIRef(value)
    return rdflib.Literal(value)

def _handle_violations(data_graph, shapes_graph, results_graph, results_text, error_msg):
    """
    Gather violation info, store it in JSON, then redirect with an error.
    """
    from rdflib.namespace import RDF
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")

    violations = []
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        focus_node = results_graph.value(result, SH.focusNode)
        result_path = results_graph.value(result, SH.resultPath)
        severity = results_graph.value(result, SH.resultSeverity)
        source_shape = results_graph.value(result, SH.sourceShape)
        message = results_graph.value(result, SH.resultMessage)
        min_count = results_graph.value(result, SH.minCount)

        # Convert blank-node property shapes to their parent node shape:
        if isinstance(source_shape, rdflib.BNode):
            parent_shapes = list(shapes_graph.subjects(predicate=SH.property, object=source_shape))
            if parent_shapes:
                source_shape = parent_shapes[0]

        violations.append({
            "focus_node": str(focus_node) if focus_node else None,
            "result_path": str(result_path) if result_path else None,
            "severity": str(severity) if severity else None,
            "source_shape": str(source_shape) if source_shape else None,
            "message": str(message) if message else None,
            "min_count": str(min_count) if min_count else None,
        })

    overview = build_shape_overview(data_graph, shapes_graph, violations)
    with open(SHACL_OVERVIEW_JSON, "w") as f:
        json.dump({"overview": overview, "violations": violations}, f, indent=2)

    merged_triples = [(str(s), str(p), str(o)) for (s, p, o) in data_graph]
    with open(LAST_UPLOADED_FILE_JSON, "w") as f:
        json.dump(merged_triples, f, indent=2)

    return redirect(url_for("index", error=error_msg, error_details=results_text))


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
            "q": source["q"]
        }
        mobile_sources.append(fill_template(moso, **mosodata))

    featuremembers = ''.join(mobile_sources) + calcpoint
    metadata = {"name": form_data["name"], "year": form_data["year"], "featuremembers": featuremembers}

    return fill_template(featcoll, **metadata)


#App routes for Shacl
@app.route("/")
def index():
    error = request.args.get("error")
    error_details = request.args.get("error_details")
    success = request.args.get("success")

    uploaded_triples = []
    if os.path.exists(LAST_UPLOADED_FILE_JSON):
        with open(LAST_UPLOADED_FILE_JSON, "r") as f:
            uploaded_triples = json.load(f)

    conformance_overview = []
    shacl_violations = []
    if os.path.exists(SHACL_OVERVIEW_JSON):
        with open(SHACL_OVERVIEW_JSON, "r") as f:
            data = json.load(f)
            conformance_overview = data.get("overview", [])
            shacl_violations = data.get("violations", [])

    # Build dictionary for shapes
    shapes_graph = rdflib.Graph()
    shapes_graph.parse(SHAPES_FILE_PATH, format="turtle")
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")

    shape_property_map = {}
    shape_targetclass_map = {}
    for shape_node in shapes_graph.subjects(rdflib.RDF.type, SH.NodeShape):
        shape_uri = str(shape_node)
        prop_paths = []
        for prop_bnode in shapes_graph.objects(shape_node, SH.property):
            p = shapes_graph.value(prop_bnode, SH.path)
            if p:
                prop_paths.append(str(p))
        shape_property_map[shape_uri] = prop_paths

        tc = shapes_graph.value(shape_node, SH.targetClass)
        if tc:
            shape_targetclass_map[shape_uri] = str(tc)
        else:
            shape_targetclass_map[shape_uri] = ""

    # Build shape->list of focus nodes from violations
    shape_violation_map = {}
    for v in shacl_violations:
        shape = v["source_shape"]
        focus_node = v["focus_node"]
        if shape and focus_node:
            if shape not in shape_violation_map:
                shape_violation_map[shape] = []
            shape_violation_map[shape].append(focus_node)

    return render_template(
        "index.html",
        error=error,
        error_details=error_details,
        success=success,
        uploaded_triples=uploaded_triples,
        new_document_triples=added_triples_history,
        conformance_overview=conformance_overview,
        shacl_violations=shacl_violations,
        shape_property_map=shape_property_map,
        shape_violation_map=shape_violation_map,
        shape_targetclass_map=shape_targetclass_map,
        enumerate=enumerate,
    )

@app.template_filter('frag')
def frag(uri: str) -> str:
    """
    Return the part after '#', used to shorten URIs in templates.
    """
    if '#' in uri:
        return uri.rsplit('#', 1)[-1]
    return uri

@app.route("/upload_and_validate", methods=["POST"])
def upload_and_validate():
    """
    Handle a newly uploaded .ttl file, do SHACL validation, and insert if conforming.
    """
    if "nen_file" not in request.files:
        return redirect(url_for("index", error="No file part in request."))

    file = request.files["nen_file"]
    if not file or file.filename == "":
        return redirect(url_for("index", error="No file selected."))
    if not file.filename.endswith(".ttl"):
        return redirect(url_for("index", error="Please upload a .ttl file."))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        ttl_data = f.read()

    data_graph = rdflib.Graph()
    data_graph.parse(data=ttl_data, format="turtle")

    # Merge in-memory new doc
    for (s, p, o) in added_triples_history:
        data_graph.add((rdflib.URIRef(s), rdflib.URIRef(p), rdflib.Literal(o)))

    # Parse shapes
    shapes_graph = rdflib.Graph()
    shapes_graph.parse(SHAPES_FILE_PATH, format="turtle")

    # Validate
    conforms, results_graph, results_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        serialize_report_graph=False
    )

    if conforms:
        # Insert into GraphDB
        graph_uri = f"http://example.org/graphs/{file.filename}"
        try:
            update_query = construct_insert_query(graph_uri, ttl_data)
            sparql_update(update_query)
        except Exception as e:
            return redirect(url_for("index", error=f"Insertion to GraphDB failed: {str(e)}"))

        # Save merged data
        merged_triples = [(str(s), str(p), str(o)) for (s, p, o) in data_graph]
        with open(LAST_UPLOADED_FILE_JSON, "w") as f:
            json.dump(merged_triples, f, indent=2)

        # Reset SHACL info
        with open(SHACL_OVERVIEW_JSON, "w") as f:
            json.dump({"overview": [], "violations": []}, f)

        return redirect(url_for("index", success="File uploaded and validated successfully!"))

    # If not conforming => gather violations
    return _handle_violations(data_graph, shapes_graph, results_graph, results_text, "SHACL validation failed.")

@app.route("/revalidate", methods=["POST"])
def revalidate():
    """
    Re-run SHACL validation on the last validated data + new doc in memory.
    """
    if not os.path.exists(LAST_UPLOADED_FILE_JSON):
        return redirect(url_for("index", error="No previously uploaded data to revalidate."))

    with open(LAST_UPLOADED_FILE_JSON, "r") as f:
        triple_list = json.load(f)

    data_graph = rdflib.Graph()
    for (s, p, o) in triple_list:
        data_graph.add(
            (rdflib.URIRef(s), rdflib.URIRef(p), create_rdflib_node(o))
        )

    # Add new doc
    for (s, p, o) in added_triples_history:
        data_graph.add(
            (rdflib.URIRef(s), rdflib.URIRef(p), create_rdflib_node(o))
        )

    shapes_graph = rdflib.Graph()
    shapes_graph.parse(SHAPES_FILE_PATH, format="turtle")

    conforms, results_graph, results_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        serialize_report_graph=False
    )

    if conforms:
        final_triples = [(str(s), str(p), str(o)) for (s, p, o) in data_graph]
        with open(LAST_UPLOADED_FILE_JSON, "w") as f:
            json.dump(final_triples, f, indent=2)

        with open(SHACL_OVERVIEW_JSON, "w") as f:
            json.dump({"overview": [], "violations": []}, f)

        return redirect(url_for("index", success="Revalidation successful! No more SHACL errors."))
    else:
        return _handle_violations(data_graph, shapes_graph, results_graph, results_text, "Revalidation found SHACL violations.")

@app.route("/add_missing_data", methods=["POST"])
def add_missing_data():
    shape_uri = request.form.get("shape_uri", "").strip()
    focus_node = request.form.get("focus_node", "").strip()
    manual_focus_val = request.form.get("manual_focus_node", "").strip()
    predicate = request.form.get("predicate", "").strip()
    object_value = request.form.get("object_value", "").strip()
    target_class = request.form.get("target_class", "").strip()

    # Wizard fields for MobileSource
    mosolabel = request.form.get("mosolabel_wiz", "").strip()
    mosoposition = request.form.get("mosoposition_wiz", "").strip()
    sectorid = request.form.get("sectorid_wiz", "").strip()
    emitsNH3 = request.form.get("emitsNH3_wiz", "").strip()
    emitsNOX = request.form.get("emitsNOX_wiz", "").strip()
    emitsPM10 = request.form.get("emitsPM10_wiz", "").strip()
    emitsNO2 = request.form.get("emitsNO2_wiz", "").strip()

    # Optional sub-wizard for the same MobileSource
    sms_mobtype = request.form.get("wizard_sms_mobtype", "").strip()
    sms_fuelyear = request.form.get("wizard_sms_fuelyear", "").strip()
    sms_desc = request.form.get("wizard_sms_description", "").strip()

    # Wizard fields for SpecificMobileSource
    sm_mobtype = request.form.get("mobtype_wiz", "").strip()
    sm_fuelyear = request.form.get("fuelyear_wiz", "").strip()
    sm_description = request.form.get("description_wiz", "").strip()

    # 1) If user chose "Manual Focus Node," build a real URI
    if focus_node == "MANUAL_FOCUS":
        # If they typed an absolute URI => keep it
        # Else prefix it with e.g. "http://example.org/test-data#"
        if manual_focus_val.startswith("http://") or manual_focus_val.startswith("https://"):
            focus_node = manual_focus_val
        else:
            focus_node = f"http://example.org/test-data#{manual_focus_val}"

    if not shape_uri or not focus_node:
        return redirect(url_for("index", error="No shape or focus node selected."))

    # 2) If shape = MobileSourceShape & user filled wizard => create all props
    if shape_uri.endswith("MobileSourceShape") and (
        mosolabel or mosoposition or sectorid or emitsNH3 or emitsNOX or emitsPM10 or emitsNO2
    ):
        # type triple
        added_triples_history.append(
            (focus_node, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
             "http://example.org/graphs/aerius-extension#MobileSource")
        )

        # add properties, converting numeric fields
        if mosolabel:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#mosolabel", mosolabel))
        if mosoposition:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#mosoposition", mosoposition))
        if sectorid:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#sectorid", sectorid))

        # parse numeric
        if emitsNH3:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#emitsNH3",
                                          parse_numeric(emitsNH3)))
        if emitsNOX:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#emitsNOX",
                                          parse_numeric(emitsNOX)))
        if emitsPM10:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#emitsPM10",
                                          parse_numeric(emitsPM10)))
        if emitsNO2:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#emitsNO2",
                                          parse_numeric(emitsNO2)))

        # sub-wizard for creating a single SpecificMobileSource
        if sms_mobtype or sms_fuelyear or sms_desc:
            # create a new node for the SpecificMobileSource
            sm_uri = f"http://example.org/test-data#SMS_{uuid.uuid4().hex[:6]}"  # or generate a user-provided name
            added_triples_history.append(
                (focus_node, "http://example.org/graphs/aerius-extension#hasSpecificMobileSource", sm_uri)
            )
            added_triples_history.append(
                (sm_uri, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                 "http://example.org/graphs/aerius-extension#SpecificMobileSource")
            )
            if sms_mobtype:
                added_triples_history.append((sm_uri, "http://example.org/graphs/aerius-extension#mobtype", sms_mobtype))
            if sms_fuelyear:
                added_triples_history.append((sm_uri, "http://example.org/graphs/aerius-extension#fuelyear",
                                             parse_numeric(sms_fuelyear)))
            if sms_desc:
                added_triples_history.append((sm_uri, "http://example.org/graphs/aerius-extension#description", sms_desc))

        return redirect(url_for("index", success="MobileSource wizard data added!"))

    # 3) If shape = SpecificMobileSourceShape => create it
    if shape_uri.endswith("SpecificMobileSourceShape") and (sm_mobtype or sm_fuelyear or sm_description):
        # type triple
        added_triples_history.append(
            (focus_node, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
             "http://example.org/graphs/aerius-extension#SpecificMobileSource")
        )
        if sm_mobtype:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#mobtype", sm_mobtype))
        if sm_fuelyear:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#fuelyear",
                                         parse_numeric(sm_fuelyear)))
        if sm_description:
            added_triples_history.append((focus_node, "http://example.org/graphs/aerius-extension#description", sm_description))

        return redirect(url_for("index", success="SpecificMobileSource wizard data added!"))

    # 4) Fallback single property approach
    if predicate and object_value:
        # Single triple approach
        added_triples_history.append((focus_node, predicate, parse_numeric_or_uri(object_value)))

        # If shape has a target class => type triple
        if target_class:
            added_triples_history.append((focus_node, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", target_class))

        # If property == hasEmissionSource => type object as EmissionSource
        if predicate == "http://example.org/graphs/aerius-extension#hasEmissionSource":
            added_triples_history.append((
                object_value,
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                "http://example.org/graphs/aerius-extension#EmissionSource"
            ))

        return redirect(url_for("index", success="Single triple data added!"))

    # 5) No data
    return redirect(url_for("index", error="No wizard fields or single property provided."))

@app.route("/delete_new_triple", methods=["POST"])
def delete_new_triple():
    """
    Remove a triple from the new doc in memory.
    """
    idx_str = request.form.get("triple_index")
    try:
        idx = int(idx_str)
        if 0 <= idx < len(added_triples_history):
            del added_triples_history[idx]
            return redirect(url_for("index", success="Triple deleted."))
        else:
            return redirect(url_for("index", error="Invalid triple index."))
    except Exception as e:
        return redirect(url_for("index", error=str(e)))

@app.route("/shacl_constraints")
def shacl_constraints():
    """
    A simpler page listing all NodeShapes from the SHACL file.
    """
    if not os.path.exists(SHAPES_FILE_PATH):
        return redirect(url_for("index", error="SHACL shapes file not found."))

    shapes_data = rdflib.Graph()
    try:
        shapes_data.parse(SHAPES_FILE_PATH, format="turtle")
    except Exception as e:
        return redirect(url_for("index", error=f"Error parsing shapes: {e}"))

    from rdflib.namespace import RDF
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")

    all_shacl_constraints = []
    for shape_node in shapes_data.subjects(RDF.type, SH.NodeShape):
        shape_name = str(shape_node)
        target_class = shapes_data.value(shape_node, SH.targetClass)
        for prop in shapes_data.objects(shape_node, SH.property):
            path = shapes_data.value(prop, SH.path)
            msg = shapes_data.value(prop, SH.message)
            all_shacl_constraints.append({
                "shape_name": shape_name,
                "target_class": str(target_class) if target_class else "",
                "path": str(path) if path else "",
                "message": str(msg) if msg else ""
            })

    return render_template("shacl_constraints.html", all_shacl_constraints=all_shacl_constraints)


#App routes for AERIUS API
@app.route('/aerius', methods=['GET', 'POST'])
def aerius():
    projectfoler = "./project files"
    ontology_files = [f for f in os.listdir(projectfoler) if f.endswith(".ttl")]
    selected_ontology = request.args.get("ontology_file", ontology_files[0] if ontology_files else None)

    if selected_ontology:
        ontology_path = os.path.join(projectfoler, selected_ontology)
    else:
        ontology_path = None

    if ontology_path:
        g = rdflib.Graph()
        g.parse(ontology_path, format="turtle")
    else:
        g = rdflib.Graph()

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
            mobile_sources = list(g.objects(activity, rdflib.URIRef("http://example.org/graphs/aerius-extension#hasEmissionSource")))
            for mobile_source in mobile_sources:
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
                "specific_sources": [],
                "q": i + 1
            }

            # Handle specific mobile sources
            for j, specific in enumerate(source["specific_sources"]):
                updated_specific = {
                    "mobtype": request.form.get(f"mobtype_{i}_{j}", specific["mobtype"]),
                    "fuelyear": request.form.get(f"fuelyear_{i}_{j}", specific["fuelyear"]),
                    "description": request.form.get(f"description_{i}_{j}", specific["description"]),
                    "fueloruse": 'literFuelPerYear' if str(specific["mobtype"]) in ['B2T', 'B4T', 'LPG'] else 'operatingHoursPerYear'
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
            jobs[job_key] = {"status": "RUNNING", "files": [], "name": form_data["name"]}
            flash("Calculation started. Job key added to status section.")
        else:
            flash("Failed to start the calculation.")

        return redirect(url_for('aerius'))

    return render_template('Aerius UI.html', projects=projects, selected_project=selected_project, form_data=form_data, jobs=jobs, ontology_files=ontology_files, selected_ontology=selected_ontology)

@app.route('/aerius/check_status/<job_key>/<job_name>', methods=['GET'])
def check_status(job_key, job_name):
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
                jobs[job_key] = {"status": "completed", "files": pdf_files, "folder": job_key, "name": job_name}
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
