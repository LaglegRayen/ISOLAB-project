// Clients page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthentication();
    
    // Load clients data
    loadClientsData();
    
    // Initialize search and filters
    initializeSearch();
    
    // Initialize modal
    initializeModal();
});

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

let allClients = [];

async function loadClientsData() {
    try {
        // Load clients from API

        const response = await fetch('/clients/all', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (response.ok) {
            const result = await response.json();
            allClients = result.data || [];
        } else {
            console.error('Failed to load clients from API');
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
    
    clients.forEach(client => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <strong>${client.nom || '-'}</strong><br>
                <small style="color: #65676b;">${client.prenom || '-'}</small>
            </td>
            <td>${client.prenom || '-'}</td>
            <td>${client.telephone || '-'}</td>
            <td>${client.adresse || '-'}</td>
            <td>${client.location || '-'}</td>
            <td><span class="status-badge ${getTypeClass(client.type)}">${client.type || '-'}</span></td>
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
        return (client.nom && client.nom.toLowerCase().includes(searchTerm)) ||
               (client.prenom && client.prenom.toLowerCase().includes(searchTerm)) ||
               (client.telephone && client.telephone.toLowerCase().includes(searchTerm));
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
    document.getElementById('modalSociety').textContent = client.society;
    document.getElementById('modalManager').textContent = client.manager;
    document.getElementById('modalFiscalNumber').textContent = client.fiscalNumber;
    document.getElementById('modalPhone').textContent = client.phone;
    document.getElementById('modalEmail').textContent = client.email;
    document.getElementById('modalAddress').textContent = client.address;
    document.getElementById('modalLocation').textContent = client.location;
    document.getElementById('modalType').textContent = client.type;
    
    // Show client machines
    const machinesContainer = document.getElementById('clientMachines');
    machinesContainer.innerHTML = '';
    
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
        const response = await fetch(`/clients/${clientId}`, {
            method: 'DELETE'
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
