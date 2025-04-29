from flask import Flask, request, send_file, jsonify, render_template
import os
import tempfile
from PIL import Image
from werkzeug.utils import secure_filename
from flask_cors import CORS
import requests
from PyPDF2 import PdfMerger
import requests

print("Current Working Directory:", os.getcwd())


current_folder = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            static_folder=os.path.join(current_folder, 'static'),
            template_folder=os.path.join(current_folder, 'templates'))

CORS(app)

SUPABASE_URL = "https://obxawkpojgoazkzmxbic.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ieGF3a3BvamdvYXprem14YmljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU3MDU4OTYsImV4cCI6MjA2MTI4MTg5Nn0.Q2QpKRLTXo164lazGKD4u6v-yC2xDrSb2gqqoxcdgLk"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_output_filename(original_filename, new_extension):
    base = os.path.splitext(secure_filename(original_filename))[0]
    return f"{base}.{new_extension}"

# ========== ROUTES ==========
@app.route('/')
def home1():
    return render_template('index.html')

@app.route('/download')
def download_page():
    return render_template('download.html')

@app.route('/word2pdf')
def word2pdf_page():
    return render_template('word2pdf.html')

@app.route('/pdf2word')
def pdf2word_page():
    return render_template('pdf2word.html')

@app.route('/excel2pdf')
def excel2pdf_page():
    return render_template('excel2pdf.html')

@app.route('/mergepdf')
def mergepdf_page():
    return render_template('mergepdf.html')

@app.route('/imgcnvt')
def imgcnvt_page():
    return render_template('imgcnvt.html')

@app.route('/feedback')
def feedback_page():
    return render_template('feedback.html')

@app.route('/readmorecom')
def readmore_page():
    return render_template('readmorecom.html')

# ========== CONVERSION ROUTES ==========

@app.route('/convertw2pdf', methods=['POST'])
def convert_word_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '' or not (file.filename.lower().endswith('.doc') or file.filename.lower().endswith('.docx')):
        return jsonify({"error": "Invalid file"}), 400

    try:
        files = {'file': (file.filename, file.stream, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        headers = {
            'Apikey': '6d6543fa-c7dd-4eb3-ad4a-138f299ef592'
        }

        response = requests.post(
            'https://api.cloudmersive.com/convert/docx/to/pdf',
            headers=headers,
            files=files
        )

        if response.status_code != 200:
            return jsonify({"error": f"Conversion failed: {response.text}"}), 500

        output_filename = get_output_filename(file.filename, 'pdf')
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_path.write(response.content)
        output_path.close()

        return send_file(
            output_path.name,
            as_attachment=True,
            download_name=output_filename,
            mimetype="application/pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/convertpdf2word', methods=['POST'])
def convert_pdf_to_word():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file"}), 400

    try:
        files = {'file': (file.filename, file.stream, 'application/pdf')}
        headers = {
            'Apikey': '6d6543fa-c7dd-4eb3-ad4a-138f299ef592'
        }

        response = requests.post(
            'https://api.cloudmersive.com/convert/pdf/to/docx',
            headers=headers,
            files=files
        )

        if response.status_code != 200:
            return jsonify({"error": f"Conversion failed: {response.text}"}), 500

        output_filename = get_output_filename(file.filename, 'docx')
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        output_path.write(response.content)
        output_path.close()

        return send_file(
            output_path.name,
            as_attachment=True,
            download_name=output_filename,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/excel2pdf', methods=['POST'])
def convert_excel_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '' or not (file.filename.lower().endswith('.xls') or file.filename.lower().endswith('.xlsx')):
        return jsonify({"error": "Invalid file"}), 400

    try:
        files = {'file': (file.filename, file.stream, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        headers = {
            'Apikey': '6d6543fa-c7dd-4eb3-ad4a-138f299ef592'
        }

        response = requests.post(
            'https://api.cloudmersive.com/convert/xlsx/to/pdf',
            headers=headers,
            files=files
        )

        if response.status_code != 200:
            return jsonify({"error": f"Conversion failed: {response.text}"}), 500

        output_filename = get_output_filename(file.filename, 'pdf')
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_path.write(response.content)
        output_path.close()

        return send_file(
            output_path.name,
            as_attachment=True,
            download_name=output_filename,
            mimetype="application/pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/mergepdfs', methods=['POST'])
def merge_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist('files')

    if len(files) < 2:
        return jsonify({"error": "Please upload at least two PDF files to merge."}), 400

    try:
        merger = PdfMerger()

        for file in files:
            if file.filename == '' or not file.filename.lower().endswith('.pdf'):
                return jsonify({"error": "All uploaded files must be PDFs."}), 400
            file.stream.seek(0)
            merger.append(file.stream)

        # Save the merged PDF
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        with open(output_path.name, 'wb') as f_out:
            merger.write(f_out)

        merger.close()

        # Optional: dynamic merged filename
        output_filename = "merged.pdf"

        return send_file(
            output_path.name,
            as_attachment=True,
            download_name=output_filename,
            mimetype="application/pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========== IMAGE CONVERSION ==========

@app.route('/imgcnvt', methods=['POST'])
def convert_images():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        output_format = request.form.get('format', '').lower()

        if output_format not in ALLOWED_EXTENSIONS:
            return "Invalid output format", 400

        img = Image.open(file)

        if img.mode == 'RGBA':
            img = img.convert('RGB')

        output_filename = get_output_filename(filename, output_format)
        img_io = tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}")
        img.save(img_io.name, format=output_format.upper())
        img_io.close()

        return send_file(
            img_io.name,
            mimetype=f'image/{output_format}',
            as_attachment=True,
            download_name=output_filename
        )

    return "Invalid file", 400


# ========== DATABASE ==========
def insert_file_metadata(filename, file_url):
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "filename": filename,
        "file_url": file_url,
    }
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/files",
        headers=headers,
        json=payload
    )
    return response.json()


# ========== RUN APP ==========
print("🚀 Flask is running from:", __file__)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
