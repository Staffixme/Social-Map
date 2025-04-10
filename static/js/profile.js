/**
 * profile.js - Functionality for the user profile page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    const profileTabs = document.getElementById('profileTabs');
    if (profileTabs) {
        const tabs = profileTabs.querySelectorAll('.nav-link');
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs
                tabs.forEach(t => t.classList.remove('active'));
                // Add active class to clicked tab
                this.classList.add('active');
                
                // Show the corresponding tab content
                const targetId = this.getAttribute('data-bs-target').substring(1);
                const tabContents = document.querySelectorAll('.tab-pane');
                tabContents.forEach(content => {
                    content.classList.remove('show', 'active');
                    if (content.id === targetId) {
                        content.classList.add('show', 'active');
                    }
                });
            });
        });
    }
    
    // Handle subscribe/unsubscribe button interactions
    const subscribeForm = document.querySelector('form[action*="/subscribe/"]');
    const unsubscribeForm = document.querySelector('form[action*="/unsubscribe/"]');
    
    if (subscribeForm) {
        subscribeForm.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        });
    }
    
    if (unsubscribeForm) {
        unsubscribeForm.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        });
    }
});
