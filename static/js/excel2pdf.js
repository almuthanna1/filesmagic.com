document.getElementById("convert-btn").addEventListener("click", async function() {
    const fileInput = document.getElementById("fileToUpload");
    const status = document.getElementById("status");
    const downloadLink = document.getElementById("download-link");

    function updateStatus(message, isSuccess) {
        status.innerHTML = message;
        status.style.color = isSuccess ? "blue" : "red";
    }

    if (fileInput.files.length === 0) {
        updateStatus("Please upload an Excel sheet", false);
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    updateStatus("Converting...", true);
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

        updateStatus("Conversion successful! Download the PDF below", true);
    } catch (error) {
        console.error("Error during conversion:", error);
        updateStatus("Error: " + (error.message.includes("Failed to fetch")
        ? "Unable to connect to the server. Please try again later" : error.message), false);
    }
});