document.addEventListener("DOMContentLoaded", () => {
    const queryInput = document.getElementById("query-input");
    const sendButton = document.getElementById("send-button");
    const conversationLog = document.getElementById("conversation-log"); // Changed from response-area

    const search = async () => {
        const query = queryInput.value;
        if (!query) {
            alert("Please enter a question.");
            return;
        }

        // Display the user's question
        appendMessage(query, 'user-message');
        queryInput.value = ""; // Clear the input field

        // Show a "thinking" message
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
            
            // Remove the "Thinking..." message before showing the final answer
            const thinkingMessage = document.getElementById('thinking-message');
            if(thinkingMessage) {
                thinkingMessage.remove();
            }
            
            // Display the bot's final answer
            appendMessage(data.answer, 'bot-message');

        } catch (error) {
            console.error("Error fetching results:", error);
            appendMessage(`Error: ${error.message}`, 'error-message');
        }
    };

    const appendMessage = (text, className, id = null) => {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        messageElement.textContent = text;
        if (id) {
            messageElement.id = id;
        }
        conversationLog.appendChild(messageElement);
        conversationLog.scrollTop = conversationLog.scrollHeight; // Auto-scroll to bottom
    };

    sendButton.addEventListener("click", search);
    queryInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            search();
        }
    });
});