from flask import Flask, render_template, request, redirect, flash, send_file, url_for, jsonify
import os
import zipfile
import requests
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = "uploads"
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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect form data for mobile sources and specific mobile sources
        mobile_sources = []
        mobile_source_keys = [key for key in request.form.keys() if key.startswith('mosolabel')]

        for key in mobile_source_keys:
            # Extract the index of the current mobile source
            index = key.split('_')[1]

            # Gather mobile source details
            mosolabel = request.form[f'mosolabel_{index}']
            mosoposition = request.form[f'mosoposition_{index}']
            sectorid = request.form[f'sectorid_{index}']
            mosoemissions = {
                "NH3": request.form[f'NH3_{index}'],
                "NOX": request.form[f'NOX_{index}'],
                "PM10": request.form[f'PM10_{index}'],
                "NO2": request.form[f'NO2_{index}']
            }

            # Collect specific mobile sources for this mobile source
            specmob_entries = []
            specific_source_keys = [key for key in request.form.keys() if key.startswith(f'mobtype_{index}')]

            for specific_key in specific_source_keys:
                spec_index = specific_key.split('_')[2]

                mobtype = request.form[f'mobtype_{index}_{spec_index}']
                fueloruse = 'literFuelPerYear' if mobtype in ['B2T', 'B4T', 'LPG'] else 'operatingHoursPerYear'
                fuelyear = request.form[f'fuelyear_{index}_{spec_index}']
                description = request.form[f'description_{index}_{spec_index}']

                specmob_entries.append({
                    "mobtype": mobtype,
                    "fueloruse": fueloruse,
                    "fuelyear": fuelyear,
                    "description": description
                })

            specmosos = ''.join([fill_template(specmob, **entry) for entry in specmob_entries])

            # Create mobile source data
            mosodata = {
                "label": mosolabel,
                "position": mosoposition,
                "sectorid": sectorid,
                **mosoemissions,
                "specficimobilesource": specmosos,
                'q': str(int(index) + 1)
            }
            mobile_sources.append(fill_template(moso, **mosodata))

        # Combine mobile sources and calcpoint
        featuremembers = ''.join(mobile_sources) + calcpoint

        # Metadata for feature collection
        metadata = {
            "name": request.form['name'],
            "year": request.form['year'],
            "featuremembers": featuremembers
        }

        # Generate final GML content
        gml_content = fill_template(featcoll, **metadata)

        # Save the GML file
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

        return redirect(url_for('index'))

    return render_template('combined_ui.html', jobs=jobs)

@app.route('/check_status/<job_key>', methods=['GET'])
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
    return redirect(url_for('index'))




@app.route('/view/<folder>/<filename>')
def view_file(folder, filename):
    pdf_path = os.path.join(RESULT_FOLDER, folder, filename)
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=False)
    flash("File not found.")
    return redirect('/')


@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    pdf_path = os.path.join(RESULT_FOLDER, folder, filename)
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    flash("File not found.")
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
