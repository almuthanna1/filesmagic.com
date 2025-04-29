document.getElementById("convert-btn").addEventListener("click", async function () {
    const fileInput = document.getElementById("fileToUpload");
    const status = document.getElementById("status");
    const downloadLink = document.getElementById("download-link");

    // Helper function to update status message with color
    function updateStatus(message, isSuccess) {
        status.innerHTML = message;
        status.style.color = isSuccess ? "blue" : "red"; // Blue for success, red for error
    }

    // Check if the file is selected
    if (fileInput.files.length === 0) {
        updateStatus("Please upload a Word document", false);
        return;
    }

    const file = fileInput.files[0];

    // Check if the uploaded file is a valid Word document
    if (!file.name.endsWith('.docx')) {
        updateStatus("Please upload a valid Word document (.docx)", false);
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    updateStatus("Converting...", true); // Neutral status message in blue

    try {
        // Send the file to the server for conversion
        const response = await fetch('/convertw2pdf', {  // Update with correct backend URL if needed
            method: 'POST',
            body: formData
        });

        // Check if the response status is OK
        if (!response.ok) {
            const errorMsg = response.status === 404
                ? "Server not found. Please check the server connection"
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

        // Update status with success message
        updateStatus("Conversion successful! Download the PDF below", true);

        // Revoke the blob URL after the download to free memory
        downloadLink.addEventListener('click', () => {
            setTimeout(() => URL.revokeObjectURL(url), 100);
        });
    } catch (error) {
        // Log the error to the console and update the status
        console.error("Error during conversion:", error);
        updateStatus("Error: " + (error.message.includes("Failed to fetch") 
        ? "Unable to connect to the server. Please try again later" : error.message), false);
    }
});
