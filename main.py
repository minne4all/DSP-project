from flask import Flask, render_template, jsonify, send_from_directory
import os

app = Flask(__name__)

# Path to the folder containing PDFs
PDF_FOLDER = os.path.join(os.getcwd(), 'pdfs')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_documents/<category>')
def get_documents(category):
    # For simplicity, we are not categorizing PDFs. 
    # You can implement filtering by category if needed.
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
    return jsonify({"documents": pdf_files})

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    # Serve the selected PDF from the "pdfs" folder
    return send_from_directory(PDF_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
