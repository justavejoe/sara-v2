document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("upload-form");
    const fileInput = document.getElementById("file-input");
    const messageArea = document.getElementById("message-area");
    const fileListDisplay = document.getElementById("file-list");
    const uploadButton = document.getElementById("upload-button");
    const searchForm = document.getElementById("search-form");
    const searchInput = document.getElementById("search-input");
    const conversationLog = document.getElementById("conversation-log");

    // Update file list display when files are selected
    if (fileInput) {
        fileInput.addEventListener("change", () => {
            const files = fileInput.files;
            if (files.length > 0) {
                fileListDisplay.textContent = "Selected: " + Array.from(files).map(f => f.name).join(", ");
            } else {
                fileListDisplay.textContent = "";
            }
        });
    }

    // Handle upload form submission
    if (uploadForm) {
        uploadForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const files = fileInput.files;

            if (files.length === 0) {
                messageArea.textContent = "Please select files to upload.";
                messageArea.className = "status-message error";
                return;
            }

            messageArea.textContent = `Uploading ${files.length} file(s)...`;
            messageArea.className = "status-message info";
            uploadButton.disabled = true;

            const formData = new FormData();
            for (const file of files) {
                formData.append("files", file);
            }

            try {
                // Use the /api/upload endpoint provided by the frontend service
                const response = await fetch("/api/upload", {
                    method: "POST",
                    body: formData,
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || "Upload failed.");
                }

                const result = await response.json();
                messageArea.textContent = `✅ Success! ${result.message || "Files uploaded."}`;
                messageArea.className = "status-message success";
                
                // Clear the form
                uploadForm.reset();
                fileListDisplay.textContent = "";
            } catch (error) {
                console.error("Upload process failed:", error);
                messageArea.textContent = `❌ Upload failed: ${error.message}`;
                messageArea.className = "status-message error";
            } finally {
                uploadButton.disabled = false;
            }
        });
    }

    // Handle search form submission
    if (searchForm) {
        searchForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const query = searchInput.value;
            if (!query) return;

            // Display user message
            const userMessageDiv = document.createElement("div");
            userMessageDiv.className = "message user-message";
            userMessageDiv.textContent = query;
            conversationLog.appendChild(userMessageDiv);
            searchInput.value = "";
            conversationLog.scrollTop = conversationLog.scrollHeight;

            try {
                const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || "Search failed");
                }
                const results = await response.json();
                
                // Display bot response
                const botMessageDiv = document.createElement("div");
                botMessageDiv.className = "message bot-message";
                if (results.length > 0) {
                    botMessageDiv.innerHTML = results.map(doc => 
                        `<div>
                            <strong>${doc.title}</strong><br>
                            <small>${doc.source}</small><br>
                            <p>${doc.content.replace(/\n/g, '<br>')}</p>
                        </div>`
                    ).join('<hr>');
                } else {
                    botMessageDiv.textContent = "No results found.";
                }
                conversationLog.appendChild(botMessageDiv);
                conversationLog.scrollTop = conversationLog.scrollHeight;

            } catch (error) {
                console.error("Search failed:", error);
                const errorDiv = document.createElement("div");
                errorDiv.className = "message error-message";
                errorDiv.textContent = `Error: ${error.message}`;
                conversationLog.appendChild(errorDiv);
                conversationLog.scrollTop = conversationLog.scrollHeight;
            }
        });
    }
});