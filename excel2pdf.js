document.getElementById("convert-btn").addEventListener("click", async function() {
    const fileInput = document.getElementById("fileToUpload");
    const status = document.getElementById("status");
    const downloadLink = document.getElementById("download-link");

    if (fileInput.files.length === 0) {
        status.innerHTML = "Please upload an Excel sheet.";
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    status.innerHTML = "Converting...";
    downloadLink.style.display = "none";

    try {
        const response = await fetch('/excel2pdf', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error("Server not found. Please check the server connection.");
            }
            if (response.status === 500) {
                throw new Error("Server error occurred during conversion.");
            }
            throw new Error("Conversion failed with status: " + response.status);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const disposition = response.headers.get('Content-Disposition');
        const filename = disposition ? disposition.split('filename=')[1].replace(/"/g, '') : 'converted.pdf';

        downloadLink.href = url;
        downloadLink.download = filename;
        downloadLink.style.display = "block";
        status.innerHTML = "Conversion successful! Download the PDF below.";
    } catch (error) {
        if (error.message.includes("Failed to fetch")) {
            status.innerHTML = "Error: Unable to connect to the server. Please try again later.";
        } else {
            status.innerHTML = "Error: " + error.message;
        }
    }
});