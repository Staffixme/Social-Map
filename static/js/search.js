/**
 * search.js - Functionality for the search feature
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput || !searchResults) return;
    
    let searchTimeout;
    
    // Handle search input
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchResults.classList.add('d-none');
            searchResults.innerHTML = '';
            return;
        }
        
        // Set a timeout to avoid making too many requests while the user is typing
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Handle search button click
    searchButton.addEventListener('click', function() {
        const query = searchInput.value.trim();
        
        if (query.length < 2) return;
        
        performSearch(query);
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target) && !searchButton.contains(e.target)) {
            searchResults.classList.add('d-none');
        }
    });
    
    // Function to perform the search
    function performSearch(query) {
        searchResults.innerHTML = '<div class="text-center p-3"><div class="spinner-border spinner-border-sm" role="status"></div></div>';
        searchResults.classList.remove('d-none');
        
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) {
                    searchResults.innerHTML = '<div class="p-3 text-center">No results found.</div>';
                    return;
                }
                
                // Build the results HTML
                let resultsHtml = '';
                data.forEach(place => {
                    resultsHtml += `
                        <a href="/place/${place.id}" class="search-result-item d-block text-decoration-none">
                            <div class="fw-bold">${place.name}</div>
                            <div class="text-muted small">${place.address}</div>
                            <div class="small">${place.description}</div>
                        </a>
                    `;
                });
                
                searchResults.innerHTML = resultsHtml;
            })
            .catch(error => {
                console.error('Error searching:', error);
                searchResults.innerHTML = '<div class="p-3 text-center text-danger">Error performing search.</div>';
            });
    }
});
