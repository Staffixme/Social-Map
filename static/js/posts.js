/**
 * posts.js - Functionality for handling posts and infinite scrolling
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize infinite scrolling for posts
    if (document.getElementById('postsContainer')) {
        initPostsInfiniteScroll();
    }
});

/**
 * Initialize infinite scrolling for posts
 */
function initPostsInfiniteScroll() {
    const postsContainer = document.getElementById('postsContainer');
    const loadingIndicator = document.getElementById('loadingPosts');
    
    // If these elements don't exist, return early
    if (!postsContainer || !loadingIndicator) return;
    
    let currentPage = 1;
    let isLoading = false;
    let hasMorePosts = true;
    
    // Function to check if we need to load more posts
    function checkScrollPosition() {
        if (isLoading || !hasMorePosts) return;
        
        const containerBottom = postsContainer.getBoundingClientRect().bottom;
        const isNearBottom = containerBottom <= window.innerHeight + 200;
        
        if (isNearBottom) {
            loadMorePosts();
        }
    }
    
    // Add scroll event listener
    window.addEventListener('scroll', checkScrollPosition);
    
    // Function to load more posts
    function loadMorePosts() {
        isLoading = true;
        currentPage++;
        
        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        
        fetch(`/api/posts?page=${currentPage}`)
            .then(response => response.json())
            .then(posts => {
                // Hide loading indicator
                loadingIndicator.classList.add('d-none');
                
                // If no more posts, mark as complete
                if (posts.length === 0) {
                    hasMorePosts = false;
                    return;
                }
                
                // Add the new posts to the container
                posts.forEach(post => {
                    const postHtml = `
                        <div class="post-item p-3 border-bottom">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div class="d-flex align-items-center">
                                    <a href="/user/${post.user.username}" class="me-2">
                                        <img src="${post.user.avatar}" alt="${post.user.username}" class="avatar rounded-circle">
                                    </a>
                                    <div>
                                        <a href="/user/${post.user.username}" class="text-decoration-none fw-bold">${post.user.username}</a>
                                        <div class="text-muted small">
                                            <i class="fas fa-clock me-1"></i> ${formatDate(post.created_at)}
                                            <i class="fas fa-map-marker-alt ms-2 me-1"></i> 
                                            <a href="/place/${post.place.id}" class="text-decoration-none">${post.place.name}</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <h5 class="card-title">${post.title}</h5>
                            <p class="card-text">${post.content}</p>
                            
                            ${post.media_files && post.media_files.length > 0 ? `
                            <div class="media-gallery mb-3">
                                ${post.media_files.map(mediaUrl => `
                                    <div class="media-item mb-2">
                                        ${mediaUrl.endsWith('.jpg') || mediaUrl.endsWith('.jpeg') || mediaUrl.endsWith('.png') || mediaUrl.endsWith('.gif') || mediaUrl.endsWith('.webp') ? `
                                            <img src="${mediaUrl}" alt="Post media" class="img-fluid rounded">
                                        ` : mediaUrl.endsWith('.mp4') || mediaUrl.endsWith('.webm') || mediaUrl.endsWith('.ogg') ? `
                                            <video controls class="w-100 rounded">
                                                <source src="${mediaUrl}" type="video/${mediaUrl.split('.').pop()}">
                                                Your browser does not support the video tag.
                                            </video>
                                        ` : ''}
                                    </div>
                                `).join('')}
                            </div>
                            ` : post.image_url ? `
                            <div class="post-image mb-3">
                                <img src="${post.image_url}" alt="${post.title}" class="img-fluid rounded">
                            </div>
                            ` : ''}
                            
                            <div class="d-flex justify-content-between align-items-center mt-3">
                                <div class="post-actions">
                                    <button class="btn btn-sm btn-outline-secondary me-2 like-btn" 
                                            data-post-id="${post.id}" 
                                            data-liked="${post.is_liked ? 'true' : 'false'}"
                                            ${!currentUserAuthenticated ? 'disabled' : ''}>
                                        <i class="fas fa-heart ${post.is_liked ? 'text-danger' : ''}"></i>
                                        <span class="likes-count">${post.likes_count}</span>
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary comment-btn" data-post-id="${post.id}">
                                        <i class="fas fa-comment"></i>
                                        <span class="comments-count">${post.comments_count}</span>
                                    </button>
                                </div>
                                <a href="/place/${post.place.id}" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-map-marked-alt me-1"></i> View Place
                                </a>
                            </div>
                            
                            <!-- Comment section (initially hidden) -->
                            <div class="comments-section mt-3 d-none" id="comments-${post.id}">
                                <hr>
                                <h6 class="mb-3"><i class="fas fa-comments me-2"></i> Comments</h6>
                                
                                <div class="comments-list">
                                    <p class="text-muted">No comments yet. Be the first to comment!</p>
                                </div>
                                
                                ${currentUserAuthenticated ? `
                                <form class="comment-form mt-3" data-post-id="${post.id}">
                                    <div class="input-group">
                                        <input type="text" class="form-control" placeholder="Add a comment..." required>
                                        <button class="btn btn-primary" type="submit">
                                            <i class="fas fa-paper-plane"></i>
                                        </button>
                                    </div>
                                </form>
                                ` : `
                                <div class="alert alert-info mt-3">
                                    <a href="/login" class="alert-link">Log in</a> to post a comment.
                                </div>
                                `}
                            </div>
                        </div>
                    `;
                    
                    postsContainer.insertAdjacentHTML('beforeend', postHtml);
                });
                
                // Reinitialize event listeners for new posts
                setupLikeFunctionality();
                setupCommentFunctionality();
                
                isLoading = false;
            })
            .catch(error => {
                console.error('Error loading more posts:', error);
                loadingIndicator.classList.add('d-none');
                isLoading = false;
            });
    }
    
    // Helper function to format dates
    function formatDate(dateString) {
        const date = new Date(dateString);
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }
}

// Check if the current user is authenticated (used for like buttons)
// This variable should be set in the HTML template
let currentUserAuthenticated = false;
if (document.querySelector('.like-btn:not([disabled])')) {
    currentUserAuthenticated = true;
}
