document.addEventListener("DOMContentLoaded", () => {
    // --- Existing Search Elements ---
    const queryInput = document.getElementById("query-input");
    const sendButton = document.getElementById("send-button");
    const conversationLog = document.getElementById("conversation-log");

    // --- New Upload Elements ---
    const fileInput = document.getElementById("file-input");
    const uploadButton = document.getElementById("upload-button");
    const fileListDiv = document.getElementById("file-list");
    const uploadStatusDiv = document.getElementById("upload-status");

    // --- Search Functionality (no changes) ---
    const search = async () => {
        const query = queryInput.value;
        if (!query) {
            alert("Please enter a question.");
            return;
        }
        appendMessage(query, 'user-message');
        queryInput.value = "";
        appendMessage("Thinking...", 'bot-message', 'thinking-message');
        try {
            const encodedQuery = encodeURIComponent(query);
            const searchUrl = `/api/search?query=${encodedQuery}&top_k=3`;
            const response = await fetch(searchUrl);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const thinkingMessage = document.getElementById('thinking-message');
            if(thinkingMessage) thinkingMessage.remove();
            appendMessage(data.answer, 'bot-message');
        } catch (error) {
            const thinkingMessage = document.getElementById('thinking-message');
            if(thinkingMessage) thinkingMessage.remove();
            console.error("Error fetching results:", error);
            appendMessage(`Error: ${error.message}`, 'error-message');
        }
    };

    const appendMessage = (text, className, id = null) => {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        messageElement.textContent = text;
        if (id) messageElement.id = id;
        conversationLog.appendChild(messageElement);
        conversationLog.scrollTop = conversationLog.scrollHeight;
    };

    sendButton.addEventListener("click", search);
    queryInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") search();
    });

    // --- New Upload Functionality ---
    fileInput.addEventListener('change', () => {
        fileListDiv.innerHTML = '';
        uploadStatusDiv.innerHTML = '';
        if (fileInput.files.length > 0) {
            const files = Array.from(fileInput.files);
            const names = files.map(file => file.name).join(', ');
            fileListDiv.textContent = `Selected: ${names}`;
        }
    });

    uploadButton.addEventListener('click', async () => {
        if (fileInput.files.length === 0) {
            alert('Please choose files to upload.');
            return;
        }

        uploadStatusDiv.textContent = 'Uploading...';
        uploadStatusDiv.className = 'status-message';

        const formData = new FormData();
        for (const file of fileInput.files) {
            formData.append('files', file);
        }

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || `HTTP error! Status: ${response.status}`);
            }
            
            uploadStatusDiv.textContent = `Success: ${result.message}`;
            uploadStatusDiv.className = 'status-message success';

        } catch (error) {
            console.error('Upload error:', error);
            uploadStatusDiv.textContent = `Error: ${error.message}`;
            uploadStatusDiv.className = 'status-message error';
        } finally {
            // Clear the file input and list
            fileInput.value = '';
            fileListDiv.innerHTML = '';
        }
    });
});