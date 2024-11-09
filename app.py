from flask import Flask, render_template, request, send_file, jsonify, after_this_request
from pdf2docx import Converter
import os
from docx import Document
import uuid
from weasyprint import HTML

app = Flask(__name__)

# Upload folder - use absolute path for compatibility with PythonAnywhere
UPLOAD_FOLDER = './uploads'

# Create the uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Routes for rendering the templates (unchanged)
@app.route('/changelog.html')
def changelog():
    return render_template('changelog.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def home1():
    return render_template('index.html')

@app.route('/word2pdf.html')
def word2pdf():
    return render_template('word2pdf.html')

@app.route('/pdf2word.html')
def pdf2word():
    return render_template('pdf2word.html')

# Function to convert DOCX to HTML
def docx_to_html(input_path):
    doc = Document(input_path)
    html_content = "<html><body>"
    for paragraph in doc.paragraphs:
        html_content += f"<p>{paragraph.text}</p>"
    html_content += "</body></html>"
    return html_content

# Route to handle Word to PDF conversion
@app.route('/convertw2pdf', methods=['POST'])
def convert_docx_to_pdf():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    if file:
        # Create unique directory for storing files
        unique_dir = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
        os.makedirs(unique_dir, exist_ok=True)

        # Save input file
        input_file_path = os.path.join(unique_dir, file.filename)
        file.save(input_file_path)
        
        output_file_name = f"{os.path.splitext(file.filename)[0]}.pdf"
        output_file_path = os.path.join(unique_dir, output_file_name)
        
        # Convert DOCX to HTML and then to PDF using WeasyPrint
        try:
            html_content = docx_to_html(input_file_path)
            HTML(string=html_content).write_pdf(output_file_path)

            # Check if the output PDF exists
            if not os.path.exists(output_file_path):
                return "PDF conversion failed: file not created."

            @after_this_request
            def cleanup(response):
                try:
                    os.remove(input_file_path)
                    os.remove(output_file_path)
                    os.rmdir(unique_dir)
                except Exception as e:
                    print(f"Cleanup failed: {e}")
                return response

            return send_file(output_file_path, as_attachment=True, download_name=output_file_name)
        except Exception as e:
            print(f"Conversion error: {e}")  # Log specific errors for debugging
            return "An error occurred during conversion."

# Function to handle PDF to Word conversion
@app.route('/convertpdf2word', methods=['POST'])
def convert_pdf_to_docx():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the uploaded PDF file
    pdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(pdf_file_path)

    # Convert the PDF to Word
    word_file_path = os.path.splitext(pdf_file_path)[0] + '.docx'
    try:
        converter = Converter(pdf_file_path)
        converter.convert(word_file_path, start=0, end=None)
        converter.close()

        if not os.path.exists(word_file_path):
            return jsonify({'error': 'Conversion failed, Word file not found'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return send_file(word_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
