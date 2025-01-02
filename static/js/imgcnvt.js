document.getElementById("convert-btn").addEventListener("click", async function () {
    const fileInput = document.getElementById("fileToUpload");
    const status = document.getElementById("status");
    const downloadLink = document.getElementById("download-link");

    if (fileInput.files.length === 0) {
        status.innerHTML = "Please upload an image file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("format", document.getElementById("format-select").value);

    status.innerHTML = "Converting...";

    try {
        const response = await fetch("/imgcnvt", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Conversion failed with status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        // Retrieve the Content-Disposition header to extract the filename
        const disposition = response.headers.get("Content-Disposition");
        let filename = "converted_image"; // Default filename

        if (disposition) {
            const filenameMatch = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^;"']+)/i);
            if (filenameMatch && filenameMatch[1]) {
                filename = decodeURIComponent(filenameMatch[1]);
            }
        }

        // Update the download link and trigger the download
        downloadLink.href = url;
        downloadLink.download = filename; // Set the correct filename
        downloadLink.style.display = "block";
        status.innerHTML = "Conversion successful! Download the file below.";
    } catch (error) {
        status.innerHTML = `Error: ${error.message}`;
    }
});
