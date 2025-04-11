/**
 * main.js - Common functionality for the Places Social Network
 */

document.addEventListener('DOMContentLoaded', function() {
    // Setup notifications
    setupNotifications();
    
    // Global like functionality for posts
    setupLikeFunctionality();
    
    // Global comment functionality
    setupCommentFunctionality();
});

/**
 * Set up notifications functionality
 */
function setupNotifications() {
    // Only proceed if user is logged in and the notifications elements exist
    const notificationsDropdown = document.getElementById('notificationsDropdown');
    if (!notificationsDropdown) {
        return;
    }
    
    const notificationsContainer = document.getElementById('notificationsContainer');
    const notificationBadge = document.getElementById('notificationBadge');
    
    // Ensure all elements exist before continuing
    if (!notificationsContainer || !notificationBadge) {
        console.error('Notification elements not found');
        return;
    }
    
    let notificationsLoaded = false;
    
    // Load notifications when dropdown is opened
    notificationsDropdown.addEventListener('click', function() {
        if (!notificationsLoaded) {
            loadNotifications();
            notificationsLoaded = true;
        }
    });
    
    // Function to load notifications
    function loadNotifications() {
        // Show loading indicator
        notificationsContainer.innerHTML = '<div class="text-center p-3"><div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        
        fetch('/notifications')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Ensure the container still exists
                if (!notificationsContainer) {
                    console.error('Notifications container not found during data processing');
                    return;
                }
                
                // Clear loading spinner
                notificationsContainer.innerHTML = '';
                
                if (!data || data.length === 0) {
                    notificationsContainer.innerHTML = '<div class="text-center p-3">Нет уведомлений.</div>';
                    return;
                }
                
                try {
                    // Count unread notifications
                    const unreadCount = data.filter(notification => !notification.is_read).length;
                    
                    // Show badge if there are unread notifications
                    if (unreadCount > 0 && notificationBadge) {
                        notificationBadge.classList.remove('d-none');
                    } else if (notificationBadge) {
                        notificationBadge.classList.add('d-none');
                    }
                    
                    // Add notifications to container
                    data.forEach(notification => {
                        let notificationUrl = '#';
                        
                        // Determine URL based on notification type
                        if (notification.type === 'like_post' || notification.type === 'comment_post') {
                            notificationUrl = `/post/${notification.object_id}`;
                        } else if (notification.type === 'like_place' || notification.type === 'comment_place') {
                            notificationUrl = `/place/${notification.object_id}`;
                        }
                        
                        const notificationHtml = `
                            <a href="${notificationUrl}" class="notification-item d-block text-decoration-none ${!notification.is_read ? 'unread' : ''}" data-notification-id="${notification.id}">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>${notification.content}</div>
                                    <small class="text-muted ms-2">${timeAgo(new Date(notification.created_at))}</small>
                                </div>
                            </a>
                        `;
                        
                        notificationsContainer.insertAdjacentHTML('beforeend', notificationHtml);
                    });
                    
                    // Add event listeners for marking as read
                    document.querySelectorAll('.notification-item').forEach(item => {
                        item.addEventListener('click', function(e) {
                            const notificationId = this.getAttribute('data-notification-id');
                            if (notificationId) {
                                markNotificationAsRead(notificationId);
                                
                                // If it was unread, remove the unread class
                                if (this.classList.contains('unread')) {
                                    this.classList.remove('unread');
                                }
                            }
                        });
                    });
                } catch (err) {
                    console.error('Error processing notifications data:', err);
                    notificationsContainer.innerHTML = '<div class="text-center p-3 text-danger">Что-то пошло не так.</div>';
                }
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
                if (notificationsContainer) {
                    notificationsContainer.innerHTML = '<div class="text-center p-3 text-danger">Не удалось загрузить уведомления.</div>';
                }
            });
    }
    
    // Function to mark a notification as read
    function markNotificationAsRead(notificationId) {
        if (!notificationId) return;
        
        fetch(`/mark_notification_read/${notificationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            try {
                // Decrement unread count
                const unreadItems = document.querySelectorAll('.notification-item.unread');
                if (unreadItems.length <= 1 && notificationBadge) {
                    notificationBadge.classList.add('d-none');
                }
            } catch (err) {
                console.error('Error processing notification read response:', err);
            }
        })
        .catch(error => {
            console.error('Error marking notification as read:', error);
        });
    }
}

/**
 * Setup like functionality for posts
 */
function setupLikeFunctionality() {
    const likeBtns = document.querySelectorAll('.like-btn');
    
    if (likeBtns.length > 0) {
        likeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                if (btn.disabled) return;
                
                const postId = this.getAttribute('data-post-id');
                if (!postId) return;
                
                const icon = this.querySelector('i');
                const likesCount = this.querySelector('.likes-count');
                
                if (!icon || !likesCount) return;
                
                fetch(`/like_post/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    try {
                        if (data.action === 'liked') {
                            icon.classList.add('text-danger');
                            this.setAttribute('data-liked', 'true');
                        } else {
                            icon.classList.remove('text-danger');
                            this.setAttribute('data-liked', 'false');
                        }
                        likesCount.textContent = data.likes_count;
                    } catch (err) {
                        console.error('Error processing like response:', err);
                    }
                })
                .catch(error => {
                    console.error('Error liking post:', error);
                });
            });
        });
    }
    
    const likePlaceBtns = document.querySelectorAll('.like-place-btn');
    
    if (likePlaceBtns.length > 0) {
        likePlaceBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                if (btn.disabled) return;
                
                const placeId = this.getAttribute('data-place-id');
                if (!placeId) return;
                
                const icon = this.querySelector('i');
                const likesCount = this.querySelector('.place-likes-count');
                
                if (!icon || !likesCount) return;
                
                fetch(`/like_place/${placeId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    try {
                        if (data.action === 'liked') {
                            icon.classList.add('text-danger');
                            this.setAttribute('data-liked', 'true');
                        } else {
                            icon.classList.remove('text-danger');
                            this.setAttribute('data-liked', 'false');
                        }
                        likesCount.textContent = data.likes_count;
                    } catch (err) {
                        console.error('Error processing like response:', err);
                    }
                })
                .catch(error => {
                    console.error('Error liking place:', error);
                });
            });
        });
    }
}

/**
 * Setup comment functionality
 */
function setupCommentFunctionality() {
    // Toggle comment sections
    const commentBtns = document.querySelectorAll('.comment-btn');
    if (commentBtns.length > 0) {
        commentBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const postId = this.getAttribute('data-post-id');
                const commentsSection = document.getElementById(`comments-${postId}`);
                
                if (commentsSection) {
                    if (commentsSection.classList.contains('d-none')) {
                        commentsSection.classList.remove('d-none');
                    } else {
                        commentsSection.classList.add('d-none');
                    }
                }
            });
        });
    }
    
    // Submit comment forms
    const commentForms = document.querySelectorAll('.comment-form');
    if (commentForms.length > 0) {
        commentForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();

                const postId = this.getAttribute('data-post-id');
                if (!postId) return;

                const input = this.querySelector('input');
                if (!input) return;

                const content = input.value;
                if (content.trim() === '') return;

                const formData = new FormData();
                formData.append('content', content);

                fetch(`/comment_post/${postId}`, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        try {
                            // Add the new comment to the list
                            const commentsSection = document.getElementById(`comments-${postId}`);
                            if (!commentsSection) return;

                            const commentsList = commentsSection.querySelector('.comments-list');
                            if (!commentsList) return;

                            const emptyMessage = commentsList.querySelector('p.text-muted');
                            if (emptyMessage) {
                                emptyMessage.remove();
                            }

                            const comment = data.comment;
                            const commentHtml = `
                                <div class="comment-item d-flex mb-3">
                                    <a href="/user/${comment.user.username}" class="me-2">
                                        <img src="${comment.user.avatar}" alt="${comment.user.username}" class="avatar avatar-sm rounded-circle">
                                    </a>
                                    <div class="comment-content">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <a href="/user/${comment.user.username}" class="text-decoration-none fw-bold">${comment.user.username}</a>
                                            <small class="text-muted">${comment.created_at}</small>
                                        </div>
                                        <p class="mb-0">${comment.content}</p>
                                    </div>
                                </div>
                            `;

                            commentsList.insertAdjacentHTML('beforeend', commentHtml);

                            // Update the comments count
                            const commentsCountElement = document.querySelector(`button[data-post-id="${postId}"] .comments-count`);
                            if (commentsCountElement) {
                                commentsCountElement.textContent = parseInt(commentsCountElement.textContent) + 1;
                            }

                            // Clear the input
                            input.value = '';
                        } catch (err) {
                            console.error('Error processing comment response:', err);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error submitting comment:', error);
                });
            });
        });
    }
}

/**
 * Helper function to format dates in a friendly "time ago" format
 */
function timeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = Math.floor(seconds / 31536000);
    if (interval >= 1) {
        return interval + " year" + (interval === 1 ? "" : "s") + " ago";
    }
    
    interval = Math.floor(seconds / 2592000);
    if (interval >= 1) {
        return interval + " month" + (interval === 1 ? "" : "s") + " ago";
    }
    
    interval = Math.floor(seconds / 86400);
    if (interval >= 1) {
        return interval + " day" + (interval === 1 ? "" : "s") + " ago";
    }
    
    interval = Math.floor(seconds / 3600);
    if (interval >= 1) {
        return interval + " hour" + (interval === 1 ? "" : "s") + " ago";
    }
    
    interval = Math.floor(seconds / 60);
    if (interval >= 1) {
        return interval + " minute" + (interval === 1 ? "" : "s") + " ago";
    }
    
    return "just now";
}
