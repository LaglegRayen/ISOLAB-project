
// API base URL for Google Cloud Run service
var API_BASE_URL = window.API_BASE_URL || 'https://my-service-83716313182.europe-central2.run.app';
window.API_BASE_URL = API_BASE_URL;

// Default navigateTo implementation if not provided elsewhere
if (typeof navigateTo !== 'function') {
    function navigateTo(page) {
        // Map logical page names to endpoint routes
        const endpointMap = {
            'dashboard': 'https://isolab-support.firebaseapp.com/dashboard.html',
            'my-tasks': 'https://isolab-support.firebaseapp.com/dashboard.html#myTasksContainer',
            'machines': 'https://isolab-support.firebaseapp.com/voir-machines.html',
            'clients': 'https://isolab-support.firebaseapp.com/clients.html',
            'users': 'https://isolab-support.firebaseapp.com/users.html'
        };
        const target = endpointMap[page] || ('/' + page);
        window.location.href = target;
    }
}

// Role-based navigation configuration
function configureNavigationByRole(userRole) {
    const adminOnlyItems = ['nav-users-item', 'nav-clients-item'];
    const adminOnlyButtons = ['nav-add-client', 'nav-add-client-item']; // Individual buttons that need hiding
    const deliveryManagerItems = ['nav-add-machine-item']; // Items for delivery managers
    
    // Hide admin-only items for non-admin users
    if (userRole !== 'admin') {
        adminOnlyItems.forEach(itemId => {
            const item = document.getElementById(itemId);
            if (item) {
                item.style.display = 'none';
            }
        });
        
        // Hide admin-only buttons (these are <a> tags, not <li> tags)
        adminOnlyButtons.forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) {
                // Hide the parent <li> element if it exists
                const parentLi = button.closest('li');
                if (parentLi) {
                    parentLi.style.display = 'none';
                } else {
                    // Hide the button itself if no parent <li>
                    button.style.display = 'none';
                }
            }
        });
    }
    
    // Hide delivery manager items for non-delivery managers and non-admins
    if (userRole !== 'admin' && userRole !== 'delivery_manager') {
        deliveryManagerItems.forEach(itemId => {
            const item = document.getElementById(itemId);
            if (item) item.style.display = 'none';
        });
    }
}

// Check user authentication and configure navigation
async function checkAuthAndConfigureNav() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/current`, { 
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (response.ok) {
            const data = await response.json();
            if (data.role) {
                // Add a small delay to ensure DOM is ready
                setTimeout(() => {
                    configureNavigationByRole(data.role);
                }, 100);
            }
        }
    } catch (error) {
        console.log('Auth check failed:', error);
    }
}


// Logout functionality for all pages
function handleLogout() {
    fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        console.log('Logout response:', data);
        sessionStorage.removeItem('currentUser');
        window.location.href = 'https://isolab-support.firebaseapp.com/login.html';
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
        'nav-machines': 'machines',
        'nav-clients': 'clients',
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
    
    // Configure navigation based on user role
    checkAuthAndConfigureNav();

});
