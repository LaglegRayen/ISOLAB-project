// Landing page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Dashboard button: check authentication via API before navigating
    var dashboardBtn = document.getElementById('dashboardBtn');
    if (dashboardBtn) {
        dashboardBtn.addEventListener('click', function() {
            fetch('api/users/current')
                .then(res => res.json())
                .then(data => {
                    if (!data.error) {
                        window.location.href = 'html/dashboard.html';
                    } else {
                        alert('Vous devez être connecté pour accéder au tableau de bord.');
                    }
                })
                .catch(() => {
                    alert('Erreur de connexion.');
                });
        });
    }

    // Login button: call API to get login page
    var quickLoginBtn = document.getElementById('quickLoginBtn');
    if (quickLoginBtn) {
        quickLoginBtn.addEventListener('click', function() {
            fetch('/goto-login', { method: 'GET' })
                .then(response => {
                    if (response.ok) {
                        // Redirect to the login page using the same URL
                        window.location.href = response.url;
                    } else {
                        alert('Impossible d\'accéder à la page de connexion.');
                    }
                })
                .catch(() => {
                    alert('Erreur lors de la tentative d\'accès à la page de connexion.');
                });
        });
    }
});

