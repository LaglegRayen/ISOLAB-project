// Login functionality
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    // Handle form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleLogin();
    });
});

function handleLogin() {
    const email = document.getElementById('email').value;
    // Basic validation
    if (!email) {
        showError('Veuillez entrer votre email');
        return;
    }
    // Show loading state
    const submitBtn = document.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = 'Connexion...';
    submitBtn.disabled = true;
    // Simulate login process
    setTimeout(() => {
        // For demo purposes, accept any email
        localStorage.setItem('user', JSON.stringify({
            email: email,
            loginTime: new Date().toISOString()
        }));
        // Redirect to dashboard
        window.location.href = '../html/dashboard.html';
    }, 800);
}


function showError(message) {
    // Show error in the dedicated error div
    const errorDiv = document.getElementById('loginError');
    if (errorDiv) {
        errorDiv.textContent = message;
        setTimeout(() => {
            errorDiv.textContent = '';
        }, 4000);
    }
}
