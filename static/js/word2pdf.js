document.getElementById("convert-btn").addEventListener("click", async function () {
    const fileInput = document.getElementById("fileToUpload");
    const status = document.getElementById("status");
    const downloadLink = document.getElementById("download-link");

    // Check if the file is selected
    if (fileInput.files.length === 0) {
        status.innerHTML = "Please upload a Word document.";
        return;
    }

    const file = fileInput.files[0];

    // Check if the uploaded file is a valid Word document
    if (!file.name.endsWith('.docx')) {
        status.innerHTML = "Please upload a valid Word document (.docx).";
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    status.innerHTML = "Converting...";

    try {
        // Send the file to the server for conversion
        const response = await fetch('/convertw2pdf', {  // Update with correct backend URL if needed
            method: 'POST',
            body: formData
        });

        // Check if the response status is OK
        if (!response.ok) {
            const errorMsg = response.status === 404
                ? "Server not found. Please check the server connection."
                : response.status === 500
                ? "Server error occurred during conversion."
                : "Conversion failed with status: " + response.status;
            throw new Error(errorMsg);
        }

        // Get the response blob (converted PDF file)
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        // Log the disposition header to check the filename (for debugging)
        const disposition = response.headers.get('Content-Disposition');
        console.log('Content-Disposition:', disposition); // Log the disposition header for debugging

        // Extract the filename from the Content-Disposition header
        const filename = disposition && disposition.includes('filename=') 
            ? disposition.split('filename=')[1].replace(/"/g, '')
            : 'converted.pdf';

        // Set the download link for the PDF
        downloadLink.href = url;
        downloadLink.download = filename;
        downloadLink.style.display = "block";

        // Update status
        status.innerHTML = "Conversion successful! Download the PDF below.";

        // Revoke the blob URL after the download to free memory
        downloadLink.addEventListener('click', () => {
            setTimeout(() => URL.revokeObjectURL(url), 100);
        });
    } catch (error) {
        // Log the error to the console and update the status
        console.error("Error during conversion:", error);
        status.innerHTML = "Error: " + (error.message.includes("Failed to fetch") 
            ? "Unable to connect to the server. Please try again later." 
            : error.message);
    }
});