// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    checkAuthentication();
    
    // Load dashboard data
    loadDashboardData();
    
    // Initialize dashboard components
    initializeDashboard();
});

function checkAuthentication() {
    const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = 'login.html';
        return;
    }
}

async function loadDashboardData() {
    try {
        // Load stats from API
        await updateStatCards();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function updateStatCards() {
    try {
        // Get clients count
        const clientsResponse = await fetch('/api/clients');
        const clientsData = await clientsResponse.json();
        const totalClients = clientsData.success ? (clientsData.data || []).length : 0;
        
        // Get machines count
        const machinesResponse = await fetch('/api/machines');
        const machinesData = await machinesResponse.json();
        const machines = machinesData.success ? (machinesData.data || []) : [];
        const totalMachines = machines.length;
        const activeMachines = machines.filter(m => m.status === 'actif' || m.status === 'active').length;
        const maintenanceMachines = machines.filter(m => m.status === 'maintenance').length;
        
        // Update display
        document.getElementById('totalMachines').textContent = totalMachines;
        document.getElementById('activeMachines').textContent = activeMachines;
        document.getElementById('maintenanceMachines').textContent = maintenanceMachines;
        document.getElementById('totalClients').textContent = totalClients;
        
    } catch (error) {
        console.error('Error updating stats:', error);
        // Set default values on error
        document.getElementById('totalMachines').textContent = '0';
        document.getElementById('activeMachines').textContent = '0';
        document.getElementById('maintenanceMachines').textContent = '0';
        document.getElementById('totalClients').textContent = '0';
    }
}

function initializeDashboard() {
    // Add click handlers for stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('click', function() {
            const title = this.querySelector('.stat-info p').textContent;
            handleStatCardClick(title);
        });
    });
}

function handleStatCardClick(title) {
    switch(title) {
        case 'Total machines':
            window.location.href = 'voir-machines.html';
            break;
        case 'Machines actives':
            window.location.href = 'voir-machines.html?status=active';
            break;
        case 'En maintenance':
            window.location.href = 'maintenance.html';
            break;
        case 'Clients':
            window.location.href = 'clients.html';
            break;
    }
}
