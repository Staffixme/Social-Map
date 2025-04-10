/**
 * auth.js - Functionality for authentication pages (login/register)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Form validation for login form
    const loginForm = document.querySelector('form[action*="/login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            // Validate email
            const email = document.getElementById('email').value;
            if (!validateEmail(email)) {
                e.preventDefault();
                showValidationError('email', 'Please enter a valid email address.');
                return;
            }
            
            // Validate password
            const password = document.getElementById('password').value;
            if (password.length < 1) {
                e.preventDefault();
                showValidationError('password', 'Please enter your password.');
                return;
            }
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging in...';
            submitButton.disabled = true;
        });
    }
    
    // Form validation for registration form
    const registerForm = document.querySelector('form[action*="/register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            // Validate username
            const username = document.getElementById('username').value;
            if (username.length < 3) {
                e.preventDefault();
                showValidationError('username', 'Username must be at least 3 characters long.');
                return;
            }
            
            // Validate email
            const email = document.getElementById('email').value;
            if (!validateEmail(email)) {
                e.preventDefault();
                showValidationError('email', 'Please enter a valid email address.');
                return;
            }
            
            // Validate password
            const password = document.getElementById('password').value;
            if (password.length < 6) {
                e.preventDefault();
                showValidationError('password', 'Password must be at least 6 characters long.');
                return;
            }
            
            // Validate password confirmation
            const password2 = document.getElementById('password2').value;
            if (password !== password2) {
                e.preventDefault();
                showValidationError('password2', 'Passwords do not match.');
                return;
            }
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registering...';
            submitButton.disabled = true;
        });
    }
    
    // Helper function to validate email
    function validateEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }
    
    // Helper function to show validation errors
    function showValidationError(fieldId, message) {
        const field = document.getElementById(fieldId);
        field.classList.add('is-invalid');
        
        // Check if error message element already exists
        let errorElement = field.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.insertBefore(errorElement, field.nextSibling);
        }
        
        errorElement.textContent = message;
        
        // Add event listener to clear error on input
        field.addEventListener('input', function() {
            this.classList.remove('is-invalid');
        }, { once: true });
    }
    
    // Password visibility toggle
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordField = document.getElementById(this.getAttribute('data-target'));
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            
            // Toggle icon
            const icon = this.querySelector('i');
            if (type === 'text') {
                icon.className = 'fas fa-eye-slash';
            } else {
                icon.className = 'fas fa-eye';
            }
        });
    });
});
