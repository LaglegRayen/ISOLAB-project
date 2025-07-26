// Add Machine page functionality - Simplified
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthentication();
    
    // Initialize form
    initializeForm();
    
    // Load clients for selection
    loadClients();
});

function checkAuthentication() {
    const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = 'login.html';
        return;
    }
}

let allClients = [];

function initializeForm() {
    const form = document.getElementById('addMachineForm');
    
    // Add form submission handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormSubmission();
    });
    
    // Add basic validation
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

async function loadClients() {
    try {
        const response = await fetch('/api/clients');
        if (response.ok) {
            const result = await response.json();
            allClients = result.data || [];
            setupClientSearch();
        }
    } catch (error) {
        console.error('Error loading clients:', error);
    }
}

function setupClientSearch() {
    const clientSearch = document.getElementById('clientSearch');
    const searchResults = document.getElementById('clientSearchResults');
    
    if (!clientSearch || !searchResults) return;
    
    clientSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        
        if (searchTerm.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        
        const filteredClients = allClients.filter(client => 
            (client.nom && client.nom.toLowerCase().includes(searchTerm)) ||
            (client.prenom && client.prenom.toLowerCase().includes(searchTerm))
        );
        
        displaySearchResults(filteredClients);
    });
}

function displaySearchResults(clients) {
    const searchResults = document.getElementById('clientSearchResults');
    
    if (clients.length === 0) {
        searchResults.style.display = 'none';
        return;
    }
    
    searchResults.innerHTML = '';
    clients.forEach(client => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        resultItem.innerHTML = `
            <strong>${client.nom} ${client.prenom}</strong><br>
            <small>${client.telephone} - ${client.location}</small>
        `;
        resultItem.addEventListener('click', () => selectClient(client));
        searchResults.appendChild(resultItem);
    });
    
    searchResults.style.display = 'block';
}

let selectedClientData = null;

function selectClient(client) {
    selectedClientData = client;
    
    // Update search input
    document.getElementById('clientSearch').value = `${client.nom} ${client.prenom}`;
    
    // Hide search results
    document.getElementById('clientSearchResults').style.display = 'none';
    
    // Show selected client info
    const selectedClient = document.getElementById('selectedClient');
    if (selectedClient) {
        selectedClient.innerHTML = `
            <div class="client-info">
                <h4>${client.nom} ${client.prenom}</h4>
                <p><i class="fas fa-phone"></i> ${client.telephone}</p>
                <p><i class="fas fa-map-marker-alt"></i> ${client.location}</p>
            </div>
        `;
        selectedClient.style.display = 'block';
    }
    
    // Add hidden input for clientId
    let clientIdInput = document.getElementById('selectedClientId');
    if (!clientIdInput) {
        clientIdInput = document.createElement('input');
        clientIdInput.type = 'hidden';
        clientIdInput.id = 'selectedClientId';
        clientIdInput.name = 'clientId';
        document.getElementById('addMachineForm').appendChild(clientIdInput);
    }
    clientIdInput.value = client.id;
}

function populateClientSelect() {
    const clientSelect = document.getElementById('clientId');
    if (!clientSelect) {
        // If there's no clientId select, create client search functionality
        return;
    }
    
    clientSelect.innerHTML = '<option value="">Sélectionner un client</option>';
    
    allClients.forEach(client => {
        const option = document.createElement('option');
        option.value = client.id;
        option.textContent = `${client.nom} ${client.prenom}`;
        clientSelect.appendChild(option);
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
    const form = document.getElementById('addMachineForm');
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
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
    
    const formData = getFormData();
    saveMachine(formData);
}

function getFormData() {
    const form = document.getElementById('addMachineForm');
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

async function saveMachine(machineData) {
    try {
        showNotification('Enregistrement en cours...', 'info');
        
        // Format data for API - map HTML form fields to API fields
        const apiData = {
            serialNumber: machineData.serialNumber,
            machineType: machineData.machineType,
            marque: machineData.marque || '',
            modele: machineData.modele || '',
            puissance: machineData.puissance || '',
            status: machineData.machineStatus || 'actif', // HTML uses machineStatus
            clientId: machineData.clientId || '',
            prixHT: parseFloat(machineData.prixHT) || 0,
            prixTTC: parseFloat(machineData.prixTTC) || 0
        };
        
        const response = await fetch('/api/machines', {
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
        console.log('Machine enregistrée:', result);
        
        showNotification('Machine ajoutée avec succès!', 'success');
        resetForm();
        
    } catch (error) {
        console.error('Erreur:', error);
        showNotification(`Erreur: ${error.message}`, 'error');
    }
}

function resetForm() {
    const form = document.getElementById('addMachineForm');
    form.reset();
    
    // Clear client selection
    selectedClientData = null;
    document.getElementById('clientSearch').value = '';
    document.getElementById('clientSearchResults').style.display = 'none';
    
    const selectedClient = document.getElementById('selectedClient');
    if (selectedClient) {
        selectedClient.style.display = 'none';
    }
    
    // Remove hidden clientId input
    const clientIdInput = document.getElementById('selectedClientId');
    if (clientIdInput) {
        clientIdInput.remove();
    }
    
    // Clear all error messages and styling
    const errorMessages = form.querySelectorAll('.error-message');
    errorMessages.forEach(msg => msg.remove());
    
    const errorFields = form.querySelectorAll('.error');
    errorFields.forEach(field => field.classList.remove('error'));
    
    // Focus on first input
    document.getElementById('serialNumber').focus();
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

// Modal and navigation functions for HTML compatibility
function previewMachine() {
    // Simple preview - just validate and save directly
    handleFormSubmission();
}

function closePreviewModal() {
    // Not needed in simplified version
}

function confirmAddMachine() {
    // Not needed in simplified version - save happens directly
}

function closeSuccessModal() {
    // Reset form after successful save
    resetForm();
}

function addAnotherMachine() {
    // Reset form to add another machine
    resetForm();
    showNotification('Prêt à ajouter une nouvelle machine', 'info');
}

function goToMachinesList() {
    // Navigate to machines list
    window.location.href = 'voir-machines.html';
}

function cancelAddMachine() {
    if (confirm('Êtes-vous sûr de vouloir annuler ? Toutes les données saisies seront perdues.')) {
        window.location.href = 'dashboard.html';
    }
}
