// Template System for OLIVIA
class OliviaTemplate {
    constructor() {
        this.currentPage = window.location.pathname.split('/').pop();
        this.init();
    }

    init() {
        // // Ensure navigation is consistent across all pages
        // this.setupNavigation();
        // Set active navigation item
        this.setActiveNavItem();
        // Initialize tooltips
        this.initializeTooltips();
    }

    // setupNavigation() {
    //     // Check if navigation exists
    //     const navbar = document.querySelector('.sidebar-nav');
    //     if (!navbar) return;

    //     // Ensure all navigation items have proper IDs and structure
    //     const navItems = navbar.querySelectorAll('a');
    //     navItems.forEach(item => {
    //         const href = item.getAttribute('href');
            
    //         // Set proper IDs based on href
    //         if (href === 'dashboard.html') {
    //             item.id = 'nav-dashboard';
    //         } else if (href === 'voir-machines.html') {
    //             item.id = 'nav-machines';
    //         } else if (href === 'clients.html') {
    //             item.id = 'nav-clients';
    //         } else if (href === '../index.html') {
    //             item.id = 'nav-logout';
    //         }
    //     });
    // }

    setActiveNavItem() {
        // Remove active class from all nav items
        document.querySelectorAll('.sidebar-nav a').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to current page based on URL path
        const currentPath = window.location.pathname;
        let activeNavId = '';
        
        if (currentPath.includes('dashboard')) {
            activeNavId = 'nav-dashboard';
        } else if (currentPath.includes('machines')) {
            activeNavId = 'nav-machines';
        } else if (currentPath.includes('clients')) {
            activeNavId = 'nav-clients';
        } else if (currentPath.includes('users')) {
            activeNavId = 'nav-users';
        }

        if (activeNavId) {
            const activeNav = document.getElementById(activeNavId);
            if (activeNav) {
                activeNav.classList.add('active');
            }
        }
    }

    initializeTooltips() {
        // Add tooltips to navigation items
        const navItems = document.querySelectorAll('.sidebar-nav a');
        navItems.forEach(item => {
            const text = item.textContent.trim();
            item.setAttribute('title', text);
        });
    }

    // Static method to show notifications
    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Static utility methods
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    static formatCurrency(amount) {
        return new Intl.NumberFormat('fr-TN', {
            style: 'currency',
            currency: 'TND'
        }).format(amount);
    }
}

// Initialize template system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new OliviaTemplate();
});

// Export for global use
window.OliviaTemplate = OliviaTemplate;
window.OliviaUtils = {
    showNotification: OliviaTemplate.showNotification,
    formatDate: OliviaTemplate.formatDate,
    formatCurrency: OliviaTemplate.formatCurrency
};
