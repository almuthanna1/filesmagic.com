from flask import Flask, render_template, request, send_file, jsonify, after_this_request
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from docx import Document
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
from PyPDF2 import PdfReader
import pypandoc
import tempfile
from PIL import Image
from werkzeug.utils import secure_filename
import logging


app = Flask(__name__)

# Upload folder and output folder paths
UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './output'

# Create the directories if they don't exist
os.makedirs('./uploads', exist_ok=True)
os.makedirs('./output', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER 

# Configure allowed file extensions
ALLOWED_EXTENTIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTIONS

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

@app.route('/excel2pdf.html')
def excel2pdf():
    return render_template('excel2pdf.html')

@app.route('/imgcnvt.html')
def testing():
    return render_template('imgcnvt.html')


# Route and function for Word-to-PDF conversion
@app.route('/convertw2pdf', methods=['POST'])
def convert_docx_to_pdf():
    """
    Converts a Word document (.docx) to a PDF file using python-docx and reportlab.
    """
    logger.debug("Conversion started")  # Log when conversion is called

    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    logger.debug(f"File received: {file.filename}")

    if file.filename == '':
        logger.error("No file selected")
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith('.docx'):
        logger.error("Unsupported file format. Please upload a .docx file.")
        return jsonify({"error": "Unsupported file format. Please upload a .docx file."}), 400

    try:
        # Save the uploaded Word file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file.read())
            tmp_file.close()
            logger.debug(f"Temporary file created: {tmp_file.name}")

            # Open the DOCX file with python-docx
            doc = Document(tmp_file.name)
            logger.debug(f"Word document loaded, {len(doc.paragraphs)} paragraphs found.")

            # Create a temporary PDF file using ReportLab
            output_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf_path = output_pdf.name
            output_pdf.close()
            logger.debug(f"Temporary PDF file created: {pdf_path}")

            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter

            # Write DOCX content to the PDF
            y_position = height - 40
            for para in doc.paragraphs:
                c.drawString(40, y_position, para.text)
                y_position -= 12
                if y_position <= 40:
                    c.showPage()
                    y_position = height - 40

            c.save()
            logger.debug("PDF created successfully.")

            # Send the converted PDF to the user
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"{os.path.splitext(file.filename)[0]}.pdf",
                mimetype="application/pdf"
            )
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        return jsonify({"error": f"Error during file conversion: {str(e)}"}), 500



# Route AND function to handle PDF to Word conversion
@app.route('/convertpdf2word', methods=['POST'])
def convert_pdf_to_word():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Unsupported file format. Please upload a .pdf file."}), 400

    try:
        # Get the original filename without the extension
        original_filename = os.path.splitext(file.filename)[0]

        # Read the PDF content
        pdf_reader = PdfReader(file)
        doc = Document()

        # Extract text from each page and add it to the Word document
        for page in pdf_reader.pages:
            text = page.extract_text()
            doc.add_paragraph(text)

        # Save the Word document to a buffer
        word_buffer = io.BytesIO()
        doc.save(word_buffer)

        # Move buffer's cursor to the beginning
        word_buffer.seek(0)

        # Use the original filename for the Word document
        word_filename = f"{original_filename}.docx"

        return send_file(
            word_buffer,
            as_attachment=True,
            download_name=word_filename,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Function AND route to handle Excel to PDF conversion
@app.route('/excel2pdf', methods=['POST'])
def convert_excel_to_pdf_route():
    # Check if a file is part of the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Only .xlsx files are supported'}), 400

    # Save the uploaded Excel file
    input_excel_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    print(f"Saving file to: {input_excel_path}")
    file.save(input_excel_path)

    # Set the output PDF file path
    output_pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], os.path.splitext(file.filename)[0] + '.pdf')

    try:
        # Convert the Excel file to PDF
        convert_excel_to_pdf(input_excel_path, output_pdf_path)

        # Check if the PDF was created
        if not os.path.exists(output_pdf_path):
            return jsonify({'error': 'Conversion failed, PDF file not found'}), 500

    except Exception as e:
        print(f"Error during conversion: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500

    # Return the generated PDF file
    return send_file(output_pdf_path, as_attachment=True, download_name=os.path.basename(output_pdf_path))

def convert_excel_to_pdf(input_excel, output_pdf_path):
    """Converts an Excel file to a PDF file."""
    try:
        df = pd.read_excel(input_excel)
        print(f"DataFrame: {df.head()}")  # Check DataFrame contents for debugging

        with PdfPages(output_pdf_path) as pdf:
            plt.figure(figsize=(11.69, 8.27))  # A4 size

            # Plot the dataframe
            ax = plt.gca()
            ax.axis('off')
            table = plt.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

            # Adjust table style
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.2)  # Adjust size

            # Save the plot to PDF
            pdf.savefig()
            plt.close()

    except Exception as e:
        print(f"Error in convert_excel_to_pdf function: {e}")
        raise



# Route AND function for image conversions
@app.route('/imgcnvt', methods=['POST'])
def convert_images():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    
    # Ensure a valid file was uploaded
    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        # Secure the file name
        filename = secure_filename(file.filename)
        
        # Convert the file format
        output_format = request.form['format']  # Output format chosen by the user
        img = Image.open(file)
        
        # If the image has an alpha channel (RGBA), convert it to RGB
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Prepare to save the converted image in memory
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=output_format)
        img_byte_arr.seek(0)
        
        # Set filename for the converted image
        new_filename = f"{os.path.splitext(filename)[0]}.{output_format}"
        
        # Return the image file with proper filename
        return send_file(img_byte_arr, mimetype=f'image/{output_format}', as_attachment=True, download_name=new_filename)

    return "Invalid file", 400




if __name__ == '__main__':
    app.run(debug=True)

