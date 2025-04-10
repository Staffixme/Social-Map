/**
 * places.js - Functionality for the Places page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map for adding a place
    initializeMaps();
    
    // Initialize infinite scrolling for places
    if (document.getElementById('placesContainer')) {
        initInfiniteScroll();
    }
    
    // Initialize image previews
    initImagePreviews();
});

/**
 * Initialize maps for adding places
 */
function initializeMaps() {
    // Map in the modal
    const modalMap = document.getElementById('modalMap');
    if (modalMap) {
        const map = L.map('modalMap').setView([40.7128, -74.0060], 13); // Default to New York
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        // When user clicks on the map, update the lat/lng fields
        map.on('click', function(e) {
            document.getElementById('latitude').value = e.latlng.lat.toFixed(6);
            document.getElementById('longitude').value = e.latlng.lng.toFixed(6);
            
            // Remove previous marker if exists
            map.eachLayer(function(layer) {
                if (layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });
            
            // Add a marker at the clicked location
            L.marker(e.latlng).addTo(map);
        });
        
        // When the modal is shown, refresh the map
        const addPlaceModal = document.getElementById('addPlaceModal');
        if (addPlaceModal) {
            addPlaceModal.addEventListener('shown.bs.modal', function() {
                map.invalidateSize();
            });
        }
    }
    
    // Map on the add place page
    const pageMap = document.getElementById('map');
    if (pageMap) {
        const map = L.map('map').setView([40.7128, -74.0060], 13); // Default to New York
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        // When user clicks on the map, update the lat/lng fields
        map.on('click', function(e) {
            document.getElementById('latitude').value = e.latlng.lat.toFixed(6);
            document.getElementById('longitude').value = e.latlng.lng.toFixed(6);
            
            // Remove previous marker if exists
            map.eachLayer(function(layer) {
                if (layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });
            
            // Add a marker at the clicked location
            L.marker(e.latlng).addTo(map);
        });
    }
}

/**
 * Initialize infinite scrolling for places
 */
function initInfiniteScroll() {
    const placesContainer = document.getElementById('placesContainer');
    const loadingIndicator = document.getElementById('loadingPlaces');
    
    let currentPage = 1;
    let isLoading = false;
    let hasMorePlaces = true;
    
    // Function to check if we need to load more places
    function checkScrollPosition() {
        if (isLoading || !hasMorePlaces) return;
        
        const containerBottom = placesContainer.getBoundingClientRect().bottom;
        const isNearBottom = containerBottom <= window.innerHeight + 200;
        
        if (isNearBottom) {
            loadMorePlaces();
        }
    }
    
    // Add scroll event listener
    window.addEventListener('scroll', checkScrollPosition);
    
    // Function to load more places
    function loadMorePlaces() {
        isLoading = true;
        currentPage++;
        
        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        
        fetch(`/api/places?page=${currentPage}`)
            .then(response => response.json())
            .then(places => {
                // Hide loading indicator
                loadingIndicator.classList.add('d-none');
                
                // If no more places, mark as complete
                if (places.length === 0) {
                    hasMorePlaces = false;
                    return;
                }
                
                // Add the new places to the container
                places.forEach(place => {
                    const placeHtml = `
                        <div class="col">
                            <div class="card h-100">
                                ${place.image_url ? `
                                <div class="card-img-top position-relative" style="height: 160px; overflow: hidden;">
                                    <img src="${place.image_url}" alt="${place.name}" class="img-fluid w-100 h-100" style="object-fit: cover;">
                                </div>
                                ` : ''}
                                <div class="card-body">
                                    <div class="d-flex justify-content-between">
                                        <h5 class="card-title">
                                            <a href="/place/${place.id}" class="text-decoration-none">${place.name}</a>
                                        </h5>
                                        <div>
                                            <button class="btn btn-sm btn-outline-secondary like-place-btn" 
                                                    data-place-id="${place.id}" 
                                                    data-liked="${place.is_liked ? 'true' : 'false'}"
                                                    ${!currentUserAuthenticated ? 'disabled' : ''}>
                                                <i class="fas fa-heart ${place.is_liked ? 'text-danger' : ''}"></i>
                                                <span class="place-likes-count">${place.likes_count}</span>
                                            </button>
                                        </div>
                                    </div>
                                    <p class="card-text text-muted small">
                                        <i class="fas fa-map-marker-alt me-1"></i> ${place.address}
                                    </p>
                                    <p class="card-text">${place.description.length > 100 ? place.description.substring(0, 100) + '...' : place.description}</p>
                                </div>
                                <div class="card-footer d-flex justify-content-between align-items-center">
                                    <small class="text-muted">
                                        Added by <a href="/user/${place.user.username}" class="text-decoration-none">${place.user.username}</a>
                                    </small>
                                    <a href="/place/${place.id}" class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-info-circle me-1"></i> Details
                                    </a>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    placesContainer.insertAdjacentHTML('beforeend', placeHtml);
                });
                
                // Reinitialize like buttons for new places
                setupLikeFunctionality();
                
                isLoading = false;
            })
            .catch(error => {
                console.error('Error loading more places:', error);
                loadingIndicator.classList.add('d-none');
                isLoading = false;
            });
    }
}

/**
 * Initialize image preview functionality for place image uploads
 */
function initImagePreviews() {
    // Image preview for main form
    const placeImageInput = document.getElementById('placeImage');
    const imagePreview = document.getElementById('imagePreview');
    
    if (placeImageInput && imagePreview) {
        placeImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    imagePreview.querySelector('img').src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                
                reader.readAsDataURL(this.files[0]);
            } else {
                imagePreview.style.display = 'none';
            }
        });
    }
    
    // Image preview for modal form
    const modalPlaceImageInput = document.getElementById('modalPlaceImage');
    const modalImagePreview = document.getElementById('modalImagePreview');
    
    if (modalPlaceImageInput && modalImagePreview) {
        modalPlaceImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    modalImagePreview.querySelector('img').src = e.target.result;
                    modalImagePreview.style.display = 'block';
                };
                
                reader.readAsDataURL(this.files[0]);
            } else {
                modalImagePreview.style.display = 'none';
            }
        });
    }
}

// Check if the current user is authenticated (used for like buttons)
// This variable should be set in the HTML template
let currentUserAuthenticated = false;
if (document.querySelector('.like-place-btn:not([disabled])')) {
    currentUserAuthenticated = true;
}
