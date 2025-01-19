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
import subprocess
import comtypes.client


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
    Converts a Word document (.docx) to a PDF using Microsoft Word via comtypes.client.
    """
    logging.debug("Conversion started")

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith('.docx'):
        return jsonify({"error": "Unsupported file format. Please upload a .docx file."}), 400

    tmp_file_path = None
    output_pdf_path = None

    try:
        # Save the uploaded Word file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
            tmp_file.write(file.stream.read())  # Stream to handle large files efficiently
            tmp_file_path = tmp_file.name

        # Create a temporary path for the output PDF
        output_pdf_path = os.path.splitext(tmp_file_path)[0] + ".pdf"

        try:
            # Initialize COM for the current thread
            comtypes.CoInitialize()

            # Use comtypes.client to automate Word and convert DOCX to PDF
            word = comtypes.client.CreateObject("Word.Application")
            doc = word.Documents.Open(tmp_file_path)
            doc.SaveAs(output_pdf_path, FileFormat=17)  # FileFormat=17 for PDF
            doc.Close()
            word.Quit()

            logging.info(f"Conversion successful: {output_pdf_path}")

        except Exception as e:
            logging.error(f"Word automation failed: {e}")
            return jsonify({"error": f"Conversion failed: {str(e)}"}), 500

        finally:
            # Uninitialize COM after the Word automation is done
            comtypes.CoUninitialize()

        # Send the converted PDF to the user
        response = send_file(
            output_pdf_path,
            as_attachment=True,
            download_name=f"{os.path.splitext(file.filename)[0]}.pdf",
            mimetype="application/pdf"
        )

        # Schedule cleanup of the output PDF and the temporary Word file
        def cleanup():
            try:
                os.remove(output_pdf_path)
                logging.debug(f"Removed output PDF: {output_pdf_path}")
            except Exception as e:
                logging.error(f"Failed to remove output PDF: {e}")

            try:
                os.remove(tmp_file_path)
                logging.debug(f"Removed temporary Word file: {tmp_file_path}")
            except Exception as e:
                logging.error(f"Failed to remove temporary Word file: {e}")

        response.call_on_close(cleanup)

        return response

    except Exception as e:
        logging.error(f"Unexpected error during conversion: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        # Final cleanup in case the response.call_on_close didn't trigger
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
                logging.debug(f"Removed temporary Word file during final cleanup: {tmp_file_path}")
            except Exception as e:
                logging.error(f"Failed to remove temporary Word file during final cleanup: {e}")

        if output_pdf_path and os.path.exists(output_pdf_path):
            try:
                os.remove(output_pdf_path)
                logging.debug(f"Removed output PDF during final cleanup: {output_pdf_path}")
            except Exception as e:
                logging.error(f"Failed to remove output PDF during final cleanup: {e}")

        logging.debug("Temporary files cleaned up")



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
        logging.debug("Saving PDF to temporary file...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.read())
            tmp_file_path = tmp_file.name

        logging.debug("Initializing COM...")
        comtypes.CoInitialize()

        logging.debug("Starting Word application...")
        word = comtypes.client.CreateObject("Word.Application")
        word.Visible = False

        logging.debug("Opening PDF file in Word...")
        doc = word.Documents.Open(tmp_file_path)

        word_output_path = os.path.splitext(tmp_file_path)[0] + ".docx"
        logging.debug(f"Saving Word document to {word_output_path}...")
        doc.SaveAs(word_output_path, FileFormat=16)

        logging.debug("Closing Word document and application...")
        doc.Close()
        word.Quit()

        logging.debug("Uninitializing COM...")
        comtypes.CoUninitialize()

        logging.debug("Sending converted Word file to user...")
        with open(word_output_path, 'rb') as f:
            word_buffer = io.BytesIO(f.read())

        os.remove(tmp_file_path)
        os.remove(word_output_path)

        word_buffer.seek(0)
        return send_file(
            word_buffer,
            as_attachment=True,
            download_name=f"{os.path.splitext(file.filename)[0]}.docx",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        logging.error(f"Error during PDF to Word conversion: {e}")
        return jsonify({"error": str(e)}), 500



# Function AND route to handle Excel to PDF conversion
@app.route('/excel2pdf', methods=['POST'])
def convert_excel_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith('.xlsx') and not file.filename.endswith('.xls'):
        return jsonify({"error": "Unsupported file format. Please upload an Excel file."}), 400

    try:
        # Save the uploaded Excel file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_file.write(file.read())
            excel_path = tmp_file.name

        # Generate a temporary file path for the PDF output
        pdf_output_path = os.path.splitext(excel_path)[0] + ".pdf"

        # Initialize COM for the current thread
        comtypes.CoInitialize()

        # Create an instance of Excel application
        excel = comtypes.client.CreateObject("Excel.Application")
        excel.Visible = False  # Keep Excel invisible during the process

        # Open the Excel file
        workbook = excel.Workbooks.Open(excel_path)

        # Optimize the workbook for PDF conversion
        for sheet in workbook.Sheets:
            # Define the print area explicitly (optional, adjust as needed)
            sheet.PageSetup.PrintArea = ""

            # Set fit-to-page options for better layout
            sheet.PageSetup.Zoom = False
            sheet.PageSetup.FitToPagesWide = 1
            sheet.PageSetup.FitToPagesTall = False

            # Set page orientation (optional, based on your preference)
            sheet.PageSetup.Orientation = 2  # 2 = Landscape, 1 = Portrait

        # Export the workbook to PDF
        workbook.ExportAsFixedFormat(
            Type=0,  # PDF type
            Filename=pdf_output_path,
            Quality=0,  # Standard quality
            IncludeDocProperties=True,  # Include document properties
            IgnorePrintAreas=False,  # Preserve print areas
            OpenAfterPublish=False  # Do not open the PDF after publishing
        )

        # Close the workbook and Excel application
        workbook.Close(SaveChanges=False)
        excel.Quit()

        # Read the generated PDF into a buffer
        with open(pdf_output_path, 'rb') as pdf_file:
            pdf_buffer = io.BytesIO(pdf_file.read())

        # Cleanup temporary files
        os.remove(excel_path)
        os.remove(pdf_output_path)

        # Return the PDF as a downloadable file
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"{os.path.splitext(file.filename)[0]}.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure COM is uninitialized after the operation
        comtypes.CoUninitialize()


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
        output_format = request.form['format'].lower()  # Output format chosen by the user
        if output_format not in ALLOWED_EXTENTIONS:
            return "Invalid format", 400

        # Open the uploaded file
        img = Image.open(file)
        
        # If the image has an alpha channel (RGBA), convert it to RGB
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # Create a new filename for the converted image
        new_filename = os.path.splitext(filename)[0] + f'.{output_format}'
        
        # Prepare to save the converted image in memory
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=output_format.upper())
        img_byte_arr.seek(0)
        
        # Return the image file with proper filename
        return send_file(img_byte_arr, mimetype=f'image/{output_format}', as_attachment=True, download_name=new_filename)

    return "Invalid file", 400




if __name__ == '__main__':
    app.run(debug=True)

