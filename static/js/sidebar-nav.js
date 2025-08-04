
// Default navigateTo implementation if not provided elsewhere
if (typeof navigateTo !== 'function') {
    function navigateTo(page) {
        // Map logical page names to endpoint routes
        const endpointMap = {
            'dashboard': '/dashboard',
            'my-tasks': '/dashboard#myTasksContainer',
            'voir-machines': '/machines/view',
            'clients': '/clients',
            'users': '/users'
        };
        const target = endpointMap[page] || ('/' + page);
        window.location.href = target;
    }
}


// Logout functionality for all pages
function handleLogout() {
    fetch('http://127.0.0.1:5000/logout', {
        method: 'POST',
        credentials: 'include',
    })
    .then(res => res.json())
    .then(data => {
        console.log('Logout response:', data);
        sessionStorage.removeItem('currentUser');
        window.location.href = '/';
    })
    .catch(err => {
        console.log('Logout error:', err);
    });
}

function setupLogout() {
    const logoutBtn = document.getElementById('nav-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleLogout();
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const navMap = {
        'nav-dashboard': 'dashboard',
        'nav-my-tasks': 'my-tasks',
        'nav-machines': 'voir-machines',
        'nav-clients': 'clients',
        'nav-add-client': 'ajouter-client',
        'nav-users': 'users'
    };
    Object.entries(navMap).forEach(([id, page]) => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('click', function(e) {
                e.preventDefault();
                if (typeof navigateTo === 'function') {
                    navigateTo(page);
                } else {
                    console.warn('navigateTo function is not defined');
                }
            });
        }
    });

    // Setup logout button globally
    setupLogout();

});
