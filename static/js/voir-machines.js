// Machine viewing functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthentication();
    
    // Load all machines on page load
    loadAllMachines();
    
    // Initialize search functionality
    initializeMachineSearch();
    
    // Check if there's a machine parameter in the URL
    checkMachineParameter();
});

function checkMachineParameter() {
    const urlParams = new URLSearchParams(window.location.search);
    const machineId = urlParams.get('machine');
    
    if (machineId) {
        // If there's a machine parameter, show its details
        setTimeout(() => {
            viewMachineDetails(machineId);
        }, 1000); // Wait a bit for the machines to load first
    }
}

function checkAuthentication() {
    fetch('/users/current')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                window.location.href = '/login';
            }
        })
        .catch(() => {
            window.location.href = '/login';
        });
}

function initializeMachineSearch() {
    // Allow search on Enter key
    document.getElementById('machineSearch').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchMachine();
        }
    });
}

// Load all machines
async function loadAllMachines() {
    showLoadingState();
    
    try {
        const response = await fetch('/machines', { credentials: 'include' });
        if (!response.ok) {
            throw new Error('Erreur lors du chargement des machines');
        }
        
        const result = await response.json();
        const machines = result.data || [];
        
        displayMachinesList(machines);
        
    } catch (error) {
        console.error('Error loading machines:', error);
        showError('Erreur lors du chargement des machines');
    }
}

// Display machines list
function displayMachinesList(machines) {
    const machinesGrid = document.getElementById('machinesGrid');
    const machinesList = document.getElementById('machinesList');
    const instructions = document.getElementById('instructions');
    const machineDetails = document.getElementById('machineDetails');
    
    // Hide other sections
    instructions.style.display = 'none';
    machineDetails.style.display = 'none';
    document.getElementById('noResults').style.display = 'none';
    
    // Show machines list
    machinesList.style.display = 'block';
    
    if (!machines || machines.length === 0) {
        machinesGrid.innerHTML = `
            <div class="no-machines">
                <i class="fas fa-cogs"></i>
                <h3>Aucune machine trouvée</h3>
                <p>Il n'y a pas de machines dans le système pour le moment.</p>
            </div>
        `;
        return;
    }
    
    // Clear previous content
    machinesGrid.innerHTML = '';
    
    machines.forEach(machine => {
        const machineCard = createMachineCard(machine);
        machinesGrid.appendChild(machineCard);
    });
}

// Create machine card element
function createMachineCard(machine) {
    const card = document.createElement('div');
    card.className = 'machine-card';
    
    const statusClass = getStatusClass(machine.status);
    
    card.innerHTML = `
        <div class="machine-card-header">
            <h3 class="machine-card-title">${machine.serialNumber || 'N/A'}</h3>
            <span class="machine-card-status ${statusClass}">${machine.status || 'N/A'}</span>
        </div>
        <div class="machine-card-info">
            <p><strong>Type:</strong> ${machine.machineType || 'N/A'}</p>
            <p><strong>Client:</strong> ${machine.clientName || machine.clientSociety || 'N/A'}</p>
            <p><strong>Téléphone:</strong> ${machine.clientPhone || 'N/A'}</p>
            <p><strong>Prix HT:</strong> ${machine.prixHT ? machine.prixHT + ' DT' : 'N/A'}</p>
            ${machine.deliveryDate ? `<p><strong>Livraison:</strong> ${formatDate(machine.deliveryDate)}</p>` : ''}
        </div>
        <div class="machine-card-actions">
            <button class="btn-view" onclick="viewMachineDetails('${machine.id}')">
                <i class="fas fa-eye"></i> Voir détails
            </button>
            <button class="btn-edit" onclick="editMachine('${machine.id}')">
                <i class="fas fa-edit"></i> Modifier
            </button>
        </div>
    `;
    
    return card;
}

// View machine details
function viewMachineDetails(machineId) {
    // Find the machine in the current data
    fetch(`/machines/${machineId}`, { credentials: 'include' })
        .then(response => response.json())
        .then(result => {
            if (result.machine) {
                displayMachineDetails(result.machine);
            } else {
                alert('Machine non trouvée');
            }
        })
        .catch(error => {
            console.error('Error loading machine details:', error);
            alert('Erreur lors du chargement des détails');
        });
}

// Edit machine
function editMachine(machineId) {
    window.location.href = `/machines/edit/${machineId}`;
}

// Add new machine (button handler)
function addNewMachine() {
    openAddMachineModal();
}

// Modal functions
function openAddMachineModal() {
    document.getElementById('addMachineModal').style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

function closeAddMachineModal() {
    document.getElementById('addMachineModal').style.display = 'none';
    document.body.style.overflow = 'auto'; // Re-enable scrolling
    resetMachineForm();
}

function resetMachineForm() {
    document.getElementById('addMachineForm').reset();
    document.getElementById('selectedClientInfo').innerHTML = `
        <div class="no-client-selected">
            <i class="fas fa-building"></i>
            <p>Aucun client sélectionné</p>
            <small>Recherchez et sélectionnez un client ci-dessus</small>
        </div>
    `;
    document.getElementById('clientSearchResults').style.display = 'none';
}

// Client search functionality for modal
let selectedClient = null;

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthentication();
    
    // Load all machines on page load
    loadAllMachines();
    
    // Initialize search functionality
    initializeMachineSearch();
    
    // Initialize client search in modal
    initializeClientSearch();
});

function initializeClientSearch() {
    const clientSearch = document.getElementById('clientSearch');
    if (clientSearch) {
        clientSearch.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length >= 2) {
                searchClients(query);
            } else {
                document.getElementById('clientSearchResults').style.display = 'none';
            }
        });
    }
}

async function searchClients(query) {
    try {
        const response = await fetch('/clients', { credentials: 'include' });
        if (!response.ok) throw new Error('Erreur lors de la recherche');
        
        const result = await response.json();
        const clients = result.clients || result.data || [];
        
        // Filter clients by query
        const filteredClients = clients.filter(client => {
            const searchLower = query.toLowerCase();
            return (
                (client.society && client.society.toLowerCase().includes(searchLower)) ||
                (client.manager && client.manager.toLowerCase().includes(searchLower)) ||
                (client.phone && client.phone.includes(query))
            );
        });
        
        displayClientSearchResults(filteredClients);
        
    } catch (error) {
        console.error('Error searching clients:', error);
    }
}

function displayClientSearchResults(clients) {
    const resultsContainer = document.getElementById('clientSearchResults');
    
    if (clients.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">Aucun client trouvé</div>';
    } else {
        resultsContainer.innerHTML = clients.map(client => `
            <div class="search-result-item" onclick="selectClient('${client.id}', '${client.society}', '${client.manager}', '${client.phone}', '${client.address || ''}')">
                <div class="client-info">
                    <strong>${client.society || 'N/A'}</strong>
                </div>
                <div class="client-details">
                    <span><i class="fas fa-user"></i> ${client.manager || 'N/A'}</span>
                    <span><i class="fas fa-phone"></i> ${client.phone || 'N/A'}</span>
                    <span><i class="fas fa-map-marker"></i> ${client.location || 'N/A'}</span>
                </div>
            </div>
        `).join('');
    }
    
    resultsContainer.style.display = 'block';
}

function selectClient(id, society, manager, phone, address) {
    selectedClient = { id, society, manager, phone, address };
    
    document.getElementById('selectedClientInfo').innerHTML = `
        <div class="selected-client-info">
            <div class="client-header">
                <strong>${society}</strong>
                <button type="button" class="btn btn-small btn-secondary" onclick="clearSelectedClient()">Changer</button>
            </div>
            <div class="client-details">
                <p><strong>Gérant:</strong> ${manager}</p>
                <p><strong>Téléphone:</strong> ${phone}</p>
                <p><strong>Adresse:</strong> ${address || 'N/A'}</p>
            </div>
        </div>
    `;
    
    document.getElementById('clientSearchResults').style.display = 'none';
    document.getElementById('clientSearch').value = society;
}

function clearSelectedClient() {
    selectedClient = null;
    document.getElementById('clientSearch').value = '';
    document.getElementById('selectedClientInfo').innerHTML = `
        <div class="no-client-selected">
            <i class="fas fa-building"></i>
            <p>Aucun client sélectionné</p>
            <small>Recherchez et sélectionnez un client ci-dessus</small>
        </div>
    `;
}

// Submit machine form
async function submitMachineForm() {
    if (!selectedClient) {
        alert('Veuillez sélectionner un client');
        return;
    }
    
    const formData = {
        serialNumber: document.getElementById('serialNumber').value,
        machineType: document.getElementById('machineType').value,
        ficheNumber: document.getElementById('ficheNumber').value,
        status: document.getElementById('status').value,
        prixHT: document.getElementById('prixHT').value,
        prixTTC: document.getElementById('prixTTC').value,
        deliveryDate: document.getElementById('deliveryDate').value,
        installationDate: document.getElementById('installationDate').value,
        deliveredBy: document.getElementById('deliveredBy').value,
        installedBy: document.getElementById('installedBy').value,
        paymentType: document.getElementById('paymentType').value,
        paymentStatus: document.getElementById('paymentStatus').value,
        confirmation: document.getElementById('confirmation').value,
        facturation: document.getElementById('facturation').value,
        commentairesPaiement: document.getElementById('commentairesPaiement').value,
        itpStatus: document.getElementById('itpStatus').value,
        remarques: document.getElementById('remarques').value,
        clientId: selectedClient.id
    };
    
    // Basic validation
    if (!formData.serialNumber || !formData.machineType) {
        alert('Veuillez remplir les champs obligatoires (numéro de série et type de machine)');
        return;
    }
    
    try {
        const response = await fetch('/machines', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Machine ajoutée avec succès!');
            closeAddMachineModal();
            loadAllMachines(); // Refresh the machines list
        } else {
            alert(`Erreur: ${result.error || 'Erreur inconnue'}`);
        }
        
    } catch (error) {
        console.error('Error adding machine:', error);
        alert('Erreur lors de l\'ajout de la machine');
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('addMachineModal');
    if (event.target === modal) {
        closeAddMachineModal();
    }
});

// Show loading state
function showLoadingState() {
    const machinesGrid = document.getElementById('machinesGrid');
    const machinesList = document.getElementById('machinesList');
    
    machinesList.style.display = 'block';
    machinesGrid.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
        </div>
    `;
}

// Show error message
function showError(message) {
    const machinesGrid = document.getElementById('machinesGrid');
    const machinesList = document.getElementById('machinesList');
    
    machinesList.style.display = 'block';
    machinesGrid.innerHTML = `
        <div class="no-machines">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>Erreur</h3>
            <p>${message}</p>
            <button class="btn-primary" onclick="loadAllMachines()">Réessayer</button>
        </div>
    `;
}

// Show all machines (button handler)
function showAllMachines() {
    document.getElementById('machineSearch').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('statusFilter').value = '';
    loadAllMachines();
}

// Filter machines
function filterMachines() {
    const typeFilter = document.getElementById('typeFilter').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value.toLowerCase();
    
    // Get all machine cards
    const machineCards = document.querySelectorAll('.machine-card');
    
    machineCards.forEach(card => {
        const type = card.querySelector('.machine-card-info p:first-child').textContent.toLowerCase();
        const status = card.querySelector('.machine-card-status').textContent.toLowerCase();
        
        let showCard = true;
        
        if (typeFilter && !type.includes(typeFilter)) {
            showCard = false;
        }
        
        if (statusFilter && !status.includes(statusFilter)) {
            showCard = false;
        }
        
        card.style.display = showCard ? 'block' : 'none';
    });
}

// Machine search functionality
async function searchMachine() {
    const searchTerm = document.getElementById('machineSearch').value.trim();
    
    if (!searchTerm) {
        // If no search term, show all machines
        loadAllMachines();
        return;
    }
    
    showLoadingState();
    
    try {
        // Get all machines and filter by search term
        const response = await fetch('/machines', { credentials: 'include' });
        if (!response.ok) {
            throw new Error('Erreur lors de la recherche');
        }
        
        const result = await response.json();
        const machines = result.data || [];
        
        // Filter machines by search term
        const filteredMachines = machines.filter(machine => {
            const searchLower = searchTerm.toLowerCase();
            return (
                (machine.serialNumber && machine.serialNumber.toLowerCase().includes(searchLower)) ||
                (machine.clientName && machine.clientName.toLowerCase().includes(searchLower)) ||
                (machine.clientSociety && machine.clientSociety.toLowerCase().includes(searchLower)) ||
                (machine.machineType && machine.machineType.toLowerCase().includes(searchLower))
            );
        });
        
        if (filteredMachines.length > 0) {
            displayMachinesList(filteredMachines);
        } else {
            document.getElementById('machinesList').style.display = 'none';
            document.getElementById('noResults').style.display = 'block';
            document.getElementById('instructions').style.display = 'none';
            document.getElementById('machineDetails').style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error searching machines:', error);
        showError('Erreur lors de la recherche des machines');
    }
}

async function displayMachineDetails(machineData) {
    if (!machineData) {
        document.getElementById('noResults').style.display = 'block';
        return;
    }
    
    // Set current machine ID for workflow operations
    setCurrentMachineId(machineData.id);
    
    // Hide machines list and show details
    document.getElementById('machinesList').style.display = 'none';
    document.getElementById('instructions').style.display = 'none';
    document.getElementById('noResults').style.display = 'none';
    
    // Populate basic machine data
    document.getElementById('serialNumber').textContent = machineData.serialNumber || '-';
    document.getElementById('machineType').textContent = machineData.machineType || '-';
    document.getElementById('ficheNumber').textContent = machineData.ficheNumber || '-';
    document.getElementById('prixHT').textContent = machineData.prixHT ? `${machineData.prixHT} DT` : '-';
    document.getElementById('prixTTC').textContent = machineData.prixTTC ? `${machineData.prixTTC} DT` : '-';
    
    // Set status badge
    const statusBadge = document.getElementById('machineStatus');
    statusBadge.textContent = machineData.status || '-';
    statusBadge.className = `status-badge ${getStatusClass(machineData.status)}`;
    
    // Set client information
    document.getElementById('clientSociety').textContent = machineData.clientSociety || '-';
    document.getElementById('clientName').textContent = machineData.clientName || '-';
    document.getElementById('clientPhone').textContent = machineData.clientPhone || '-';
    document.getElementById('clientEmail').textContent = machineData.clientEmail || '-';
    document.getElementById('clientAddress').textContent = machineData.clientAddress || '-';
    document.getElementById('clientLocation').textContent = machineData.clientLocation || '-';
    
    // Set installation information
    document.getElementById('deliveryDate').textContent = formatDate(machineData.deliveryDate) || '-';
    document.getElementById('installationDate').textContent = formatDate(machineData.installationDate) || '-';
    document.getElementById('installedBy').textContent = machineData.installedBy || '-';
    document.getElementById('deliveredBy').textContent = machineData.deliveredBy || '-';
    
    // Set payment information
    document.getElementById('paymentType').textContent = machineData.paymentType || '-';
    document.getElementById('paymentStatus').textContent = machineData.paymentStatus || '-';
    document.getElementById('confirmation').textContent = machineData.confirmation || '-';
    document.getElementById('facturation').textContent = machineData.facturation || '-';
    document.getElementById('commentairesPaiement').textContent = machineData.commentairesPaiement || '-';
    document.getElementById('itpStatus').textContent = machineData.itpStatus || '-';
    
    // Set remarks
    document.getElementById('remarques').textContent = machineData.remarques || '-';
    
    // Display workflow if available
    displayWorkflowStages(machineData.workflow_instance);
    
    // Show the machine details
    document.getElementById('machineDetails').style.display = 'block';
}

function getStatusClass(status) {
    if (!status) return 'status-secondary';
    const statusLower = status.toLowerCase();
    if (statusLower.includes('terminé') || statusLower.includes('complete')) return 'status-termine';
    if (statusLower.includes('cours') || statusLower.includes('progress')) return 'status-en-cours';
    if (statusLower.includes('problème') || statusLower.includes('problem')) return 'status-probleme';
    return 'status-secondary';
}

function formatDate(dateString) {
    if (!dateString) return null;
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    } catch (e) {
        return dateString;
    }
}

function printFiche() {
    window.print();
}

function exportFiche() {
    alert('Fonction d\'export en cours de développement');
}

// Workflow management functions
function displayWorkflowStages(workflowInstance) {
    const workflowContainer = document.getElementById('workflowStages');
    
    if (!workflowInstance || !workflowInstance.stages) {
        workflowContainer.innerHTML = '<p class="no-workflow">Aucun workflow disponible pour cette machine.</p>';
        return;
    }
    
    const stages = workflowInstance.stages;
    let workflowHTML = '';
    
    stages.forEach(stage => {
        const statusIcon = getWorkflowStatusIcon(stage.status);
        const statusClass = stage.status.replace('_', '-');
        
        // Format assigned users
        const assignedUsers = stage.assigned_users || [];
        const usersHtml = assignedUsers.map(user => 
            `<span class="workflow-stage-user">${user.username}</span>`
        ).join('');
        
        // Format dates
        const startedAt = stage.started_at ? formatDate(stage.started_at) : '-';
        const completedAt = stage.completed_at ? formatDate(stage.completed_at) : '-';
        
        workflowHTML += `
            <div class="workflow-stage ${statusClass}">
                <div class="workflow-stage-icon">${statusIcon}</div>
                <div class="workflow-stage-content">
                    <div class="workflow-stage-title">${stage.label}</div>
                    <div class="workflow-stage-details">
                        Status: ${getWorkflowStatusText(stage.status)} | 
                        Durée estimée: ${stage.estimated_duration_hours}h
                        ${stage.started_at ? ` | Démarré: ${startedAt}` : ''}
                        ${stage.completed_at ? ` | Terminé: ${completedAt}` : ''}
                    </div>
                    ${usersHtml ? `<div class="workflow-stage-users">${usersHtml}</div>` : ''}
                    ${stage.notes ? `<div class="workflow-stage-notes"><small>Notes: ${stage.notes}</small></div>` : ''}
                </div>
                <div class="workflow-stage-actions">
                    ${getWorkflowActionButtons(stage)}
                </div>
            </div>
        `;
    });
    
    workflowContainer.innerHTML = workflowHTML;
}

function getWorkflowStatusIcon(status) {
    const icons = {
        'completed': '<i class="fas fa-check-circle"></i>',
        'in_progress': '<i class="fas fa-spinner fa-spin"></i>',
        'pending': '<i class="fas fa-clock"></i>',
        'blocked': '<i class="fas fa-exclamation-triangle"></i>'
    };
    return icons[status] || '<i class="fas fa-question-circle"></i>';
}

function getWorkflowStatusText(status) {
    const statusTexts = {
        'completed': 'Terminé',
        'in_progress': 'En cours',
        'pending': 'En attente',
        'blocked': 'Bloqué'
    };
    return statusTexts[status] || status;
}

function getWorkflowActionButtons(stage) {
    const status = stage.status;
    let buttons = '';
    
    if (status === 'pending') {
        buttons += `<button class="workflow-stage-btn btn-start" onclick="updateWorkflowStage('${stage.name}', 'in_progress')">
            <i class="fas fa-play"></i> Commencer
        </button>`;
    } else if (status === 'in_progress') {
        buttons += `<button class="workflow-stage-btn btn-complete" onclick="updateWorkflowStage('${stage.name}', 'completed')">
            <i class="fas fa-check"></i> Terminer
        </button>`;
        buttons += `<button class="workflow-stage-btn btn-block" onclick="updateWorkflowStage('${stage.name}', 'blocked')">
            <i class="fas fa-ban"></i> Bloquer
        </button>`;
    } else if (status === 'blocked') {
        buttons += `<button class="workflow-stage-btn btn-start" onclick="updateWorkflowStage('${stage.name}', 'in_progress')">
            <i class="fas fa-play"></i> Reprendre
        </button>`;
    }
    
    return buttons;
}

async function updateWorkflowStage(stageName, newStatus) {
    // Get current machine ID (you'll need to store this when displaying machine details)
    const currentMachineId = getCurrentMachineId();
    
    if (!currentMachineId) {
        alert('Erreur: Impossible de déterminer l\'ID de la machine');
        return;
    }
    
    try {
        const response = await fetch(`/workflows/${currentMachineId}/stage/${stageName}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                status: newStatus,
                notes: prompt('Notes (optionnel):') || ''
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert(`Étape ${stageName} mise à jour avec succès!`);
            // Reload machine details to refresh workflow
            const machineData = await fetchMachineById(currentMachineId);
            if (machineData) {
                displayMachineDetails(machineData);
            }
        } else {
            alert(`Erreur: ${result.error || 'Erreur inconnue'}`);
        }
        
    } catch (error) {
        console.error('Error updating workflow stage:', error);
        alert('Erreur lors de la mise à jour de l\'étape');
    }
}

// Helper function to get current machine ID
let currentMachineId = null;

function setCurrentMachineId(machineId) {
    currentMachineId = machineId;
}

function getCurrentMachineId() {
    return currentMachineId;
}

async function fetchMachineById(machineId) {
    try {
        const response = await fetch(`/machines/${machineId}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (response.ok) {
            const result = await response.json();
            return result.machine;
        }
        return null;
    } catch (error) {
        console.error('Error fetching machine:', error);
        return null;
    }
}
