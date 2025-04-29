document.getElementById("merge-btn").addEventListener("click", async function () {
    const fileInput = document.getElementById("filesToUpload");
    const status = document.getElementById("status");
    const downloadLink = document.getElementById("download-link");

    function updateStatus(message, isSuccess) {
        status.innerHTML = message;
        status.style.color = isSuccess ? "blue" : "red";
    }

    if (fileInput.files.length < 2) {
        updateStatus("Please upload at least two PDF files to merge.", false);
        return;
    }

    const formData = new FormData();
    for (const file of fileInput.files) {
        if (!file.name.endsWith('.pdf')) {
            updateStatus("All uploaded files must be PDFs.", false);
            return;
        }
        formData.append('files', file);
    }

    updateStatus("Merging PDFs...", true);

    try {
        const response = await fetch('/mergepdfs', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error("Merge failed with status: " + response.status);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        downloadLink.href = url;
        downloadLink.download = "merged.pdf";
        downloadLink.style.display = "block";

        updateStatus("Merge successful! Download your merged PDF below.", true);

        downloadLink.addEventListener('click', () => {
            setTimeout(() => URL.revokeObjectURL(url), 100);
        });
    } catch (error) {
        console.error("Error during merging:", error);
        updateStatus("Error: " + (error.message.includes("Failed to fetch") ? "Unable to connect to server." : error.message), false);
    }
});
