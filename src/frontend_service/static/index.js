document.addEventListener("DOMContentLoaded", () => {
    const queryInput = document.getElementById("query-input");
    const sendButton = document.getElementById("send-button");
    const responseArea = document.getElementById("response-area");

    const search = async () => {
        const query = queryInput.value;
        if (!query) {
            alert("Please enter a search query.");
            return;
        }
        responseArea.innerHTML = '<p class="status-message">Searching...</p>';
        try {
            const encodedQuery = encodeURIComponent(query);
            // The top_k parameter can be adjusted as needed
            const searchUrl = `/api/search?query=${encodedQuery}&top_k=5`;
            const response = await fetch(searchUrl);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            displayResults(data.results);
        } catch (error) {
            console.error("Error fetching results:", error);
            responseArea.innerHTML = `<p class="status-message error">Error: ${error.message}</p>`;
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
            responseArea.innerHTML = '<p class="status-message">No results found.</p>';
            return;
        }
        // Clear the response area before adding new results
        responseArea.innerHTML = ""; 
        
        results.forEach(item => {
            // Create the card container
            const card = document.createElement('div');
            card.className = 'result-card';

            // --- NOTE: Assuming the backend will provide this data soon ---
            const title = item.title || 'Title Not Available';
            const authors = item.authors ? item.authors.join(', ') : 'Authors not listed';
            const publicationDate = item.publication_date || 'Date not available';
            const sourceFile = item.source_filename || item.paper_id; // Fallback to paper_id
            
            // Populate the card with structured HTML
            card.innerHTML = `
                <h3 class="result-title">${title}</h3>
                <div class="result-metadata">
                    <p><strong>Authors:</strong> ${authors}</p>
                    <p><strong>Published:</strong> ${publicationDate}</p>
                    <p><strong>Source:</strong> ${sourceFile}</p>
                </div>
                <div class="result-content">
                    <p>${item.content.replace(/\n/g, '<br>')}</p>
                </div>
                <div class="result-similarity">
                    <span>Similarity: ${(item.similarity * 100).toFixed(1)}%</span>
                </div>
            `;
            
            responseArea.appendChild(card);
        });
    }
});