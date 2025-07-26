// Machine viewing functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthentication();
    
    // Initialize search functionality
    initializeMachineSearch();
});

function checkAuthentication() {
    const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = 'login.html';
        return;
    }
}

function initializeMachineSearch() {
    // Allow search on Enter key
    document.getElementById('machineSearch').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchMachine();
        }
    });
}

// Machine search functionality
async function searchMachine() {
    const searchTerm = document.getElementById('machineSearch').value.trim();
    
    if (!searchTerm) {
        alert('Veuillez entrer un numéro de série');
        return;
    }
    
    // Hide instructions and show loading state
    document.getElementById('instructions').style.display = 'none';
    document.getElementById('noResults').style.display = 'none';
    document.getElementById('machineDetails').style.display = 'none';
    
    try {
        // Get all machines and find by serial number
        const response = await fetch('/api/machines');
        if (!response.ok) {
            throw new Error('Erreur lors de la recherche');
        }
        
        const result = await response.json();
        const machines = result.data || [];
        
        // Find machine by serial number
        const machine = machines.find(m => 
            m.serialNumber && m.serialNumber.toLowerCase().includes(searchTerm.toLowerCase())
        );
        
        if (machine) {
            await displayMachineDetails(machine);
        } else {
            document.getElementById('noResults').style.display = 'block';
        }
        
    } catch (error) {
        console.error('Error searching machine:', error);
        alert('Erreur lors de la recherche de la machine');
    }
}

async function displayMachineDetails(machineData) {
    if (!machineData) {
        document.getElementById('noResults').style.display = 'block';
        return;
    }
    
    // Populate basic machine data
    document.getElementById('serialNumber').textContent = machineData.serialNumber || '-';
    document.getElementById('machineType').textContent = machineData.machineType || '-';
    document.getElementById('prixHT').textContent = machineData.prixHT ? `${machineData.prixHT} DT` : '-';
    document.getElementById('prixTTC').textContent = machineData.prixTTC ? `${machineData.prixTTC} DT` : '-';
    
    // Set status badge
    const statusBadge = document.getElementById('machineStatus');
    statusBadge.textContent = machineData.status || '-';
    statusBadge.className = `status-badge ${getStatusClass(machineData.status)}`;
    
    // Get client information if clientId exists
    if (machineData.clientId) {
        try {
            const clientResponse = await fetch(`/api/clients/${machineData.clientId}`);
            if (clientResponse.ok) {
                const clientResult = await clientResponse.json();
                const client = clientResult.data;
                
                document.getElementById('clientSociety').textContent = client.nom || '-';
                document.getElementById('clientName').textContent = client.prenom || '-';
                document.getElementById('clientPhone').textContent = client.telephone || '-';
                document.getElementById('clientAddress').textContent = client.adresse || '-';
                document.getElementById('clientLocation').textContent = client.location || '-';
            } else {
                // Set default values if client not found
                document.getElementById('clientSociety').textContent = '-';
                document.getElementById('clientName').textContent = '-';
                document.getElementById('clientPhone').textContent = '-';
                document.getElementById('clientAddress').textContent = '-';
                document.getElementById('clientLocation').textContent = '-';
            }
        } catch (error) {
            console.error('Error loading client data:', error);
        }
    } else {
        // No client associated
        document.getElementById('clientSociety').textContent = '-';
        document.getElementById('clientName').textContent = '-';
        document.getElementById('clientPhone').textContent = '-';
        document.getElementById('clientAddress').textContent = '-';
        document.getElementById('clientLocation').textContent = '-';
    }
    
    // Show the machine details
    document.getElementById('machineDetails').style.display = 'block';
}

function getStatusClass(status) {
    if (!status) return '';
    const statusLower = status.toLowerCase();
    if (statusLower.includes('actif') || statusLower.includes('active')) return 'status-active';
    if (statusLower.includes('maintenance')) return 'status-maintenance';
    if (statusLower.includes('problème')) return 'status-problem';
    return 'status-recent';
}

function printFiche() {
    window.print();
}

function exportFiche() {
    alert('Fonction d\'export en cours de développement');
}
