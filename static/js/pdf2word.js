document.getElementById("convert-btn").addEventListener("click", async function() {
    const fileInput = document.getElementById("fileToUpload");
    const status = document.getElementById("status");
    const downloadLink = document.getElementById("download-link");

    function updateStatus(message, isSuccess) {
        status.innerHTML = message;
        status.style.color = isSuccess ? "blue" : "red";
    }

    if (fileInput.files.length === 0) {
        updateStatus("Please upload a PDF document", false);
        return;
    }

    const formData = new FormData();
    const file = fileInput.files[0];
    formData.append('file', file);

    // Extract the original file name and change the extension to .docx
    const originalFileName = file.name;
    const newFileName = originalFileName.replace(/\.pdf$/, '.docx');

    updateStatus("Converting...", true);

    try {
        const response = await fetch('/convertpdf2word', {  // Update to your PDF to Word endpoint
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

        // Set the download link with the new filename
        downloadLink.href = url;
        downloadLink.download = newFileName;
        downloadLink.style.display = "block";
        
        updateStatus("Conversion successful! Download the Word document below", true);

    } catch (error) {
        console.error("Error during conversion:", error);
        updateStatus("Error: " + (error.message.includes("Failed to fetch")
        ? "Unable to connect to the server. Please try again later" : error.message), false);
    }
});