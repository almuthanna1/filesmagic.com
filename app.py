from flask import Flask, render_template, request, send_file, jsonify
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import os

app = Flask(__name__)

# Convert .docx to PDF with proper formatting
def convert_docx_to_pdf(docx_file):
    doc = Document(docx_file)
    
    # Create a buffer to hold the PDF data
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    
    # Get basic styling for the text
    styles = getSampleStyleSheet()
    
    # List to hold the PDF elements (text, spacers, etc.)
    content = []
    
    # Loop through the paragraphs in the Word document
    for para in doc.paragraphs:
        if para.text.strip():
            paragraph = Paragraph(para.text, styles['Normal'])
            content.append(paragraph)
            content.append(Spacer(1, 12))  # Add space between paragraphs
    
    # Build the PDF
    pdf.build(content)
    
    # Move the buffer's cursor to the start
    pdf_buffer.seek(0)
    return pdf_buffer

# Route to render the HTML form
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/word2pdf.html')
def word2pdf():
    return render_template('word2pdf.html')

# Route to handle the conversion and return the PDF with the same name
@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith(('.doc', '.docx')):
        pdf_buffer = convert_docx_to_pdf(file)
        original_filename = os.path.splitext(file.filename)[0]
        return send_file(pdf_buffer,
                         as_attachment=True,
                         download_name=f"{original_filename}.pdf",
                         mimetype='application/pdf')
    
    return jsonify({"error": "Invalid file format"}), 400


if __name__ == '__main__':
    app.run(debug=True)

