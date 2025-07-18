document.addEventListener("DOMContentLoaded", () => {
    const queryInput = document.getElementById("query-input");
    const sendButton = document.getElementById("send-button");
    const responseArea = document.getElementById("response-area");

    const search = async () => {
        const query = queryInput.value;
        if (!query) {
            alert("Please enter a question.");
            return;
        }
        responseArea.innerHTML = "Searching...";
        try {
            const encodedQuery = encodeURIComponent(query);
            const searchUrl = `/api/search?query=${encodedQuery}&top_k=3`;
            const response = await fetch(searchUrl);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            displayResults(data.results);
        } catch (error) {
            console.error("Error fetching results:", error);
            responseArea.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
    };

    sendButton.addEventListener("click", search);
    queryInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            search();
        }
    });

    function displayResults(results) {
        if (!results || results.length === 0) {
            responseArea.innerHTML = "<p>No results found.</p>";
            return;
        }
        let html = "<ul>";
        results.forEach(item => {
            html += `<li style="border-bottom: 1px solid #ccc; margin-bottom: 1em; padding-bottom: 1em;">
                <p><strong>Similarity:</strong> ${(item.similarity * 100).toFixed(2)}%</p>
                <p><strong>Source:</strong> ${item.paper_id}</p>
                <p>${item.content.replace(/\n/g, '<br>')}</p>
            </li>`;
        });
        html += "</ul>";
        responseArea.innerHTML = html;
    }
});