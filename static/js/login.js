// Login functionality
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    // Handle form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        handleLogin();
    });
    
    // Signup button and form logic
    const showSignupBtn = document.getElementById('showSignupBtn');
    const signupForm = document.getElementById('signupForm');
    if (showSignupBtn && signupForm) {
        showSignupBtn.addEventListener('click', function() {
            signupForm.style.display = signupForm.style.display === 'none' ? 'block' : 'none';
        });
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleSignup();
        });
    }
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
    // Call login API
    fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
        if (ok) {
            sessionStorage.setItem('currentUser', JSON.stringify(data.user));
            window.location.href = 'dashboard.html';
        } else {
            showError(data.error || 'Erreur de connexion');
        }
    })
    .catch(() => {
        showError('Erreur de connexion. Vérifiez votre connexion internet.');
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function handleSignup() {
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const role = document.getElementById('signupRole').value;
    if (!name || !email || !password || !role) {
        showError('Veuillez remplir tous les champs pour vous inscrire.');
        return;
    }
    const submitBtn = document.querySelector('#signupForm button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = 'Inscription...';
    submitBtn.disabled = true;
    fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password, role })
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
        if (ok) {
            alert('Inscription réussie ! Vous pouvez maintenant vous connecter.');
            document.getElementById('signupForm').reset();
            document.getElementById('signupForm').style.display = 'none';
        } else {
            showError(data.error || 'Erreur lors de l\'inscription');
        }
    })
    .catch(() => {
        showError('Erreur lors de l\'inscription. Vérifiez votre connexion internet.');
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
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
