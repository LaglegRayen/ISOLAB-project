// Add Client page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthentication();
    
    // Initialize form
    initializeForm();
    
    // Add form validation
    addFormValidation();
});

function checkAuthentication() {
    const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = 'login.html';
        return;
    }
}

function initializeForm() {
    const form = document.getElementById('addClientForm');
    
    // Add form submission handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmission();
    });
    
    // Add input event listeners for real-time validation
    const requiredFields = form.querySelectorAll('input[required], select[required], textarea[required]');
    requiredFields.forEach(field => {
        field.addEventListener('input', function() {
            validateField(this);
        });
        field.addEventListener('blur', function() {
            validateField(this);
        });
    });
    
    // Set default values
    document.getElementById('status').value = 'actif';
}

function addFormValidation() {
    // Simple validation only for required fields
    const form = document.getElementById('addClientForm');
    const requiredFields = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

function validateField(field) {
    const fieldContainer = field.closest('.form-group');
    const existingError = fieldContainer.querySelector('.error-message');
    
    // Remove existing error message
    if (existingError) {
        existingError.remove();
    }
    
    // Remove error styling
    field.classList.remove('error');
    
    // Check if field is required and empty
    if (field.hasAttribute('required') && !field.value.trim()) {
        showFieldError(field, 'Ce champ est obligatoire');
        return false;
    }
    
    return true;
}

function showFieldError(field, message) {
    const fieldContainer = field.closest('.form-group');
    
    // Add error styling
    field.classList.add('error');
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    fieldContainer.appendChild(errorDiv);
}

function validateForm() {
    const form = document.getElementById('addClientForm');
    const requiredFields = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    // Basic required field validation only
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Ce champ est obligatoire');
            isValid = false;
        } else {
            // Remove error styling if field is now valid
            field.classList.remove('error');
            const existingError = field.closest('.form-group').querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }
        }
    });
    
    return isValid;
}

function handleFormSubmission() {
    if (!validateForm()) {
        showNotification('Veuillez corriger les erreurs dans le formulaire', 'error');
        return;
    }
    
    // Show preview modal
    previewClient();
}

function previewClient() {
    if (!validateForm()) {
        showNotification('Veuillez corriger les erreurs dans le formulaire', 'error');
        return;
    }
    
    // Get form data
    const formData = getFormData();
    
    // Populate preview modal with essential fields only
    document.getElementById('previewSociety').textContent = formData.society || '-';
    document.getElementById('previewManager').textContent = formData.manager || '-';
    document.getElementById('previewType').textContent = formData.clientType || '-';
    document.getElementById('previewPhone').textContent = formData.phone || '-';
    document.getElementById('previewAddress').textContent = formData.address || '-';
    document.getElementById('previewLocation').textContent = formData.location || '-';
    
    // Show preview modal
    document.getElementById('previewModal').style.display = 'flex';
}

function getFormData() {
    const form = document.getElementById('addClientForm');
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

function closePreviewModal() {
    document.getElementById('previewModal').style.display = 'none';
}

function confirmAddClient() {
    const formData = getFormData();
    
    // Simulate saving to database
    saveClient(formData);
    
    // Close preview modal
    closePreviewModal();
    
    // Show success modal
    document.getElementById('successModal').style.display = 'flex';
}

async function saveClient(clientData) {
    try {
        // Show loading state
        showNotification('Enregistrement en cours...', 'info');
        
        // Format data for API (simplified)
        const apiData = {
            nom: clientData.society,
            prenom: clientData.manager,
            telephone: clientData.phone,
            adresse: clientData.address,
            type: clientData.clientType,
            location: clientData.location,
            status: clientData.status
        };
        
        // Send to backend API
        const response = await fetch('/api/clients', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(apiData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erreur lors de l\'enregistrement');
        }
        
        const result = await response.json();
        console.log('Client enregistré:', result);
        
        // Show success notification
        showNotification('Client ajouté avec succès!', 'success');
        
    } catch (error) {
        console.error('Erreur:', error);
        showNotification(`Erreur: ${error.message}`, 'error');
    }
}

function closeSuccessModal() {
    document.getElementById('successModal').style.display = 'none';
    // Reset form
    resetForm();
}

function addAnotherClient() {
    closeSuccessModal();
    resetForm();
    showNotification('Prêt à ajouter un nouveau client', 'info');
}

function goToClientsList() {
    window.location.href = 'clients.html';
}

function resetForm() {
    const form = document.getElementById('addClientForm');
    form.reset();
    
    // Reset default values
    document.getElementById('status').value = 'actif';
    
    // Clear all error messages and styling
    const errorMessages = form.querySelectorAll('.error-message');
    errorMessages.forEach(msg => msg.remove());
    
    const errorFields = form.querySelectorAll('.error');
    errorFields.forEach(field => field.classList.remove('error'));
    
    // Focus on first input
    document.getElementById('society').focus();
}

function cancelAddClient() {
    if (confirm('Êtes-vous sûr de vouloir annuler ? Toutes les données saisies seront perdues.')) {
        window.location.href = 'clients.html';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" class="notification-close">&times;</button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const previewModal = document.getElementById('previewModal');
    const successModal = document.getElementById('successModal');
    
    if (event.target === previewModal) {
        closePreviewModal();
    }
    
    if (event.target === successModal) {
        closeSuccessModal();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Escape key to close modals
    if (event.key === 'Escape') {
        closePreviewModal();
        closeSuccessModal();
    }
    
    // Ctrl+S to save
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        handleFormSubmission();
    }
});
