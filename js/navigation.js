// Navigation Management - Enhanced with Template System
document.addEventListener('DOMContentLoaded', function() {
    // Template system handles navigation setup
    // This file now provides additional navigation enhancements
    
    // Add navigation listeners
    addNavigationListeners();
});

function addNavigationListeners() {
    // Add click handlers for navigation items
    document.querySelectorAll('.sidebar-nav a').forEach(item => {
        item.addEventListener('click', function(e) {
            // Add loading state
            this.classList.add('loading');
            
            // Remove loading state after navigation
            setTimeout(() => {
                this.classList.remove('loading');
            }, 500);
        });
    });
}

// Legacy functions for backward compatibility
function setActiveNavItem(currentPage) {
    // This is now handled by OliviaTemplate
    console.log('setActiveNavItem is deprecated. Use OliviaTemplate instead.');
}

function initializeTooltips() {
    // This is now handled by OliviaTemplate
    console.log('initializeTooltips is deprecated. Use OliviaTemplate instead.');
}

// Utility functions (moved to template.js but kept for compatibility)
function showNotification(message, type = 'info') {
    return OliviaUtils.showNotification(message, type);
}

function formatDate(dateString) {
    return OliviaUtils.formatDate(dateString);
}

function formatCurrency(amount) {
    return OliviaUtils.formatCurrency(amount);
}

// Export functions for use in other scripts
window.OliviaUtils = window.OliviaUtils || {
    showNotification,
    formatDate,
    formatCurrency
};
