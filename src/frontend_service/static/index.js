document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("upload-form");
    const fileInput = document.getElementById("file-input");
    const messageArea = document.getElementById("message-area");

    // Handle form submission
    uploadForm.addEventListener("submit", (event) => {
        event.preventDefault(); // Prevent the default form redirect

        const files = fileInput.files;
        if (files.length === 0) {
            messageArea.textContent = "Please select a file to upload.";
            return;
        }

        // We'll upload the first selected file. This can be extended to handle multiple files.
        const fileToUpload = files[0];
        messageArea.textContent = `Uploading ${fileToUpload.name}...`;
        
        // Clear the file input for the next upload
        uploadForm.reset(); 

        uploadFile(fileToUpload, messageArea);
    });
});

/**
 * Handles the entire file upload process using a GCS signed URL.
 * @param {File} file The file object to upload.
 * @param {HTMLElement} messageArea The UI element for displaying status.
 */
async function uploadFile(file, messageArea) {
    try {
        // 1. Get the secure, signed URL from our backend
        const getUrlResponse = await fetch("/documents/generate-upload-url", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ filename: file.name }),
        });

        if (!getUrlResponse.ok) {
            const errorData = await getUrlResponse.json();
            throw new Error(errorData.error || "Could not get signed URL.");
        }

        const { signedUrl } = await getUrlResponse.json();

        // 2. Upload the file directly to Google Cloud Storage using the signed URL
        const uploadResponse = await fetch(signedUrl, {
            method: "PUT",
            headers: {
                "Content-Type": "application/pdf", // Ensure this matches the type in the backend
            },
            body: file,
        });

        if (!uploadResponse.ok) {
            throw new Error("File upload to GCS failed.");
        }

        messageArea.textContent = `✅ Success! "${file.name}" is uploaded and will be processed.`;

    } catch (error) {
        console.error("Upload process failed:", error);
        messageArea.textContent = `❌ Upload failed: ${error.message}`;
    }
}