// API base URL for Google Cloud Run service
var API_BASE_URL = window.API_BASE_URL || 'https://my-service-83716313182.europe-central2.run.app';
window.API_BASE_URL = API_BASE_URL;

// Clients page functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded - clients.js starting');
    
    // Check authentication
    checkAuthentication();
    
    // Load clients data
    console.log('About to call loadClientsData()');
    loadClientsData();
    
    // Initialize search and filters
    initializeSearch();
    
    // Initialize modal
    initializeModal();
    
    console.log('Clients page initialization complete');
});

function checkAuthentication() {
    fetch(`${API_BASE_URL}/users/current`, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                window.location.href = '/login';
                return;
            }
            
            // Check if user is admin
            if (data.role !== 'admin') {
                alert('Access denied. Only administrators can access the clients page.');
                window.location.href = 'https://isolab-support.firebaseapp.com/dashboard.html';
                return;
            }
        })
        .catch(() => {
            window.location.href = '/login';
        });
}

let allClients = [];

async function loadClientsData() {
    try {
        console.log('Loading clients data...');
        // Load clients from API

        const response = await fetch(`${API_BASE_URL}/clients/all`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('API Response:', result);
            allClients = result.clients || [];
            console.log('Clients loaded:', allClients.length);
        } else {
            console.error('Failed to load clients from API, status:', response.status);
            const errorText = await response.text();
            console.error('Error response:', errorText);
            allClients = [];
        }
    } catch (error) {
        console.error('Error loading clients:', error);
        allClients = [];
    }
    
    displayClients(allClients);
    updateClientCount(allClients.length);
}

function displayClients(clients) {
    const tbody = document.getElementById('clientsTableBody');
    tbody.innerHTML = '';
    
    if (clients.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 20px; color: #6c757d;">
                    <i class="fas fa-users"></i><br>
                    Aucun client trouvé
                </td>
            </tr>
        `;
        return;
    }
    
    clients.forEach(client => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <strong>${client.clientSociety || client.clientName || '-'}</strong><br>
                <small style="color: #65676b;">Contact: ${client.clientName || '-'}</small>
            </td>
            <td>${client.clientName || '-'}</td>
            <td>${client.clientPhone || '-'}</td>
            <td>${client.clientEmail || '-'}</td>
            <td>${client.clientLocation || '-'}</td>
            <td><span class="status-badge status-active">${client.is_active ? 'Actif' : 'Inactif'}</span></td>
            <td>-</td>
            <td>
                <button class="btn btn-primary btn-small" onclick="viewClient('${client.id}')">
                    <i class="fas fa-eye"></i> Voir
                </button>
                <button class="btn btn-danger btn-small" onclick="deleteClient('${client.id}')">
                    <i class="fas fa-trash"></i> Supprimer
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function getTypeClass(type) {
    switch(type.toLowerCase()) {
        case 'leasing':
            return 'status-recent';
        case 'direct':
            return 'status-active';
        case 'agri':
            return 'status-maintenance';
        default:
            return 'status-inactive';
    }
}

function updateClientCount(count) {
    document.getElementById('totalClientsCount').textContent = `${count} clients`;
}

function initializeSearch() {
    const searchInput = document.getElementById('clientSearch');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterClients);
    }
}

function searchClients() {
    filterClients();
}

function filterClients() {
    const searchTerm = document.getElementById('clientSearch').value.toLowerCase();
    
    if (!searchTerm) {
        displayClients(allClients);
        updateClientCount(allClients.length);
        return;
    }
    
    const filteredClients = allClients.filter(client => {
        return (client.clientName && client.clientName.toLowerCase().includes(searchTerm)) ||
               (client.clientSociety && client.clientSociety.toLowerCase().includes(searchTerm)) ||
               (client.clientPhone && client.clientPhone.toLowerCase().includes(searchTerm)) ||
               (client.clientEmail && client.clientEmail.toLowerCase().includes(searchTerm));
    });
    
    displayClients(filteredClients);
    updateClientCount(filteredClients.length);
}

function viewClient(clientId) {
    const client = allClients.find(c => c.id === clientId);
    if (client) {
        showClientModal(client);
    }
}

function showClientModal(client) {
    document.getElementById('modalClientName').textContent = client.clientName || '-';
    document.getElementById('modalClientSociety').textContent = client.clientSociety || '-';
    document.getElementById('modalClientPhone').textContent = client.clientPhone || '-';
    document.getElementById('modalClientEmail').textContent = client.clientEmail || '-';
    document.getElementById('modalClientAddress').textContent = client.clientAddress || '-';
    document.getElementById('modalClientLocation').textContent = client.clientLocation || '-';
    
    // Show client machines
    const machinesContainer = document.getElementById('clientMachines');
    machinesContainer.innerHTML = '';
    
    if (client.machines && client.machines.length > 0) {
        client.machines.forEach(machineSerial => {
            const machineDiv = document.createElement('div');
            machineDiv.className = 'machine-item';
            machineDiv.innerHTML = `
                <span class="machine-serial">${machineSerial}</span>
                <span class="status-badge status-active">Actif</span>
                <a href="voir-machines.html?serial=${machineSerial}" class="btn btn-small btn-primary">
                    <i class="fas fa-eye"></i> Voir
                </a>
            `;
            machinesContainer.appendChild(machineDiv);
        });
    } else {
        machinesContainer.innerHTML = '<p>Aucune machine pour ce client</p>';
    }
    
    document.getElementById('clientModal').style.display = 'block';
}

function closeClientModal() {
    document.getElementById('clientModal').style.display = 'none';
}

function showAddClientModal() {
    // TODO: Implement add client modal
    alert('Fonctionnalité d\'ajout de client en cours de développement');
}

function editClient() {
    // TODO: Implement edit client functionality
    alert('Fonctionnalité de modification en cours de développement');
}

async function deleteClient(clientId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce client ?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/clients/${clientId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            // Reload the clients list
            loadClientsData();
            alert('Client supprimé avec succès');
        } else {
            const errorData = await response.json();
            alert(`Erreur: ${errorData.error || 'Impossible de supprimer le client'}`);
        }
    } catch (error) {
        console.error('Error deleting client:', error);
        alert('Erreur de connexion');
    }
}

function initializeModal() {
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        const modal = document.getElementById('clientModal');
        if (e.target === modal) {
            closeClientModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeClientModal();
        }
    });
}

// Add Client Modal Functions
function openAddClientModal() {
    document.getElementById('addClientModal').style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

function closeAddClientModal() {
    document.getElementById('addClientModal').style.display = 'none';
    document.body.style.overflow = 'auto'; // Re-enable scrolling
    resetClientForm();
}

function resetClientForm() {
    document.getElementById('addClientForm').reset();
}

// Submit client form
async function submitClientForm() {
    const formData = {
        clientName: document.getElementById('clientName').value,
        clientSociety: document.getElementById('clientSociety').value,
        clientPhone: document.getElementById('clientPhone').value,
        clientEmail: document.getElementById('clientEmail').value,
        clientAddress: document.getElementById('clientAddress').value,
        clientLocation: document.getElementById('clientLocation').value
    };
    
    // Basic validation
    if (!formData.clientName || !formData.clientSociety || !formData.clientPhone || !formData.clientAddress) {
        alert('Veuillez remplir les champs obligatoires (nom du client, société, téléphone, adresse)');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/clients`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Client ajouté avec succès!');
            closeAddClientModal();
            loadClientsData(); // Refresh the clients list
        } else {
            alert(`Erreur: ${result.error || 'Erreur inconnue'}`);
        }
        
    } catch (error) {
        console.error('Error adding client:', error);
        alert('Erreur lors de l\'ajout du client');
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('addClientModal');
    if (event.target === modal) {
        closeAddClientModal();
    }
});
