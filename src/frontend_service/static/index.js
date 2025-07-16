document.addEventListener("DOMContentLoaded", () => {
    const queryInput = document.getElementById("query-input");
    const sendButton = document.getElementById("send-button");
    const responseArea = document.getElementById("response-area");

    sendButton.addEventListener("click", async () => {
        const query = queryInput.value;
        if (!query) {
            alert("Please enter a question.");
            return;
        }

        responseArea.innerHTML = "Searching...";

        try {
            // NOTE: In a real deployment, this URL would be dynamically
            // configured, but for now we will hardcode it.
            // Please replace this with your backend URL.
            const backendUrl = "PASTE_YOUR_RETRIEVAL_SERVICE_URL_HERE";

            const encodedQuery = encodeURIComponent(query);
            const searchUrl = `${backendUrl}/documents/search?query=${encodedQuery}&top_k=3`;

            // We are calling a public frontend that calls a private backend.
            // For this to work, the call must originate from the frontend service.
            // We will need to adjust our architecture to handle auth properly later.
            // For now, we will call the backend directly, which will fail due to CORS
            // but demonstrates the client-side logic.
            const response = await fetch(searchUrl);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data.results);

        } catch (error) {
            console.error("Error fetching results:", error);
            responseArea.innerHTML = `<p style="color: red;">Error: Could not fetch results. Check console for details. Your backend may not be publicly accessible.</p>`;
        }
    });

    function displayResults(results) {
        if (!results || results.length === 0) {
            responseArea.innerHTML = "<p>No results found.</p>";
            return;
        }

        let html = "<ul>";
        results.forEach(item => {
            html += `<li>
                <p><strong>Similarity:</strong> ${(item.similarity * 100).toFixed(2)}%</p>
                <p><strong>Source:</strong> ${item.paper_id}</p>
                <p>${item.content}</p>
            </li>`;
        });
        html += "</ul>";
        responseArea.innerHTML = html;
    }
});