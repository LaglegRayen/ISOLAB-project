var API_BASE_URL = window.API_BASE_URL || 'https://my-service-83716313182.europe-central2.run.app';
window.API_BASE_URL = API_BASE_URL;

// Role-Based Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication and load user data
    checkAuthentication();
    
    // Initialize dashboard components
    initializeDashboard();
    
    // Load dashboard data
    loadDashboardData();
});

function checkAuthentication() {
    fetch(`${API_BASE_URL}/users/current`, { 
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                window.location.href = '/login';
            } else {
                displayUserInfo(data);
                // Navigation configuration is handled by sidebar-nav.js
            }
        })
        .catch(() => {
            window.location.href = '/login';
        });
}

function displayUserInfo(user) {
    const userInfo = document.getElementById('userInfo');
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
    const roleName = getRoleDisplayName(user.role);
    userInfo.textContent = `${fullName} - ${roleName}`;
}

function getRoleDisplayName(role) {
    const roleNames = {
        'admin': 'Administrator',
        'supervisor': 'Supervisor',
        'assembly_tech': 'Assembly Technician',
        'testing_tech': 'Testing Technician',
        'delivery_tech': 'Delivery Technician',
        'installation_tech': 'Installation Technician'
    };
    return roleNames[role] || role || 'Utilisateur';
}

async function loadDashboardData() {
    try {
        showLoading();
        
        // Load role-based dashboard data
        await Promise.all([
            loadDashboardStats(),
            loadMyTasks(),
            loadRecentActivities()
        ]);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorMessage('Erreur lors du chargement des données');
    } finally {
        hideLoading();
    }
}

async function loadDashboardStats() {
    try {
        // Load stats from multiple endpoints
        const [stagesResponse, machinesResponse, clientsResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/stages/dashboard`, { 
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            }),
            fetch(`${API_BASE_URL}/machines`, { 
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            }),
            fetch(`${API_BASE_URL}/clients/all`, { 
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' }
            })
        ]);
        
        // Process stages data (user tasks)
        if (stagesResponse.ok) {
            const stagesData = await stagesResponse.json();
            document.getElementById('myPendingTasks').textContent = stagesData.my_pending_tasks || 0;
            document.getElementById('myCompletedTasks').textContent = stagesData.my_completed_tasks || 0;
        }
        
        // Process machines data
        if (machinesResponse.ok) {
            const machinesData = await machinesResponse.json();
            const machines = machinesData.data || [];
            
            // Count active machines (not in maintenance or problems)
            const activeMachines = machines.filter(machine => {
                const status = machine.status?.toLowerCase() || '';
                return !status.includes('maintenance') && !status.includes('problème') && !status.includes('problem');
            });
            
            // Count machines in maintenance
            const maintenanceMachines = machines.filter(machine => {
                const status = machine.status?.toLowerCase() || '';
                return status.includes('maintenance');
            });
            
            document.getElementById('totalMachines').textContent = machines.length;
            document.getElementById('activeMachines').textContent = activeMachines.length;
            document.getElementById('maintenanceMachines').textContent = maintenanceMachines.length;
        }
        
        // Process clients data
        if (clientsResponse.ok) {
            const clientsData = await clientsResponse.json();
            const clients = clientsData.clients || [];
            document.getElementById('totalClients').textContent = clients.length;
        }
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        // Set default values on error
        document.getElementById('myPendingTasks').textContent = '0';
        document.getElementById('myCompletedTasks').textContent = '0';
        document.getElementById('totalMachines').textContent = '0';
        document.getElementById('activeMachines').textContent = '0';
        document.getElementById('maintenanceMachines').textContent = '0';
        document.getElementById('totalClients').textContent = '0';
    }
}

async function loadMyTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/stages/my-tasks`, {
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load tasks');
        }
        
        const data = await response.json();
        displayMyTasks(data.tasks || []);
        
    } catch (error) {
        console.error('Error loading tasks:', error);
        displayMyTasks([]);
    }
}

async function loadRecentActivities() {
    try {
        const response = await fetch(`${API_BASE_URL}/stages/recent-activities`, {
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load recent activities');
        }
        
        const data = await response.json();
        displayRecentActivities(data.activities || []);
        
    } catch (error) {
        console.error('Error loading recent activities:', error);
        displayRecentActivities([]);
    }
}

function displayMyTasks(tasks) {
    const container = document.getElementById('myTasksContainer');
    
    if (tasks.length === 0) {
        container.innerHTML = `
            <tr>
                <td colspan="5" class="no-tasks">
                    <div style="text-align: center; padding: 20px;">
                        <i class="fas fa-check-circle"></i>
                        <h3>Aucune tâche en cours</h3>
                        <p>Toutes vos tâches sont terminées !</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    const tasksHTML = tasks.map(task => `
        <tr class="task-row" data-task-id="${task.id}" data-machine-id="${task.machine_id}">
            <td>
                <strong>${task.machine_info?.serialNumber || 'N/A'}</strong><br>
                <small>${task.machine_info?.machineType || 'Type non défini'}</small>
            </td>
            <td>${task.machine_info?.clientSociety || task.machine_info?.clientName || 'Client non défini'}</td>
            <td>
                <span class="stage-label">${task.label || task.current_stage_label || 'Étape non définie'}</span>
            </td>
            <td>
                <span class="status-badge status-${task.status || 'pending'}">${getStatusText(task.status || 'pending')}</span>
            </td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="validateTask('${task.id}', '${task.machine_id}')">
                    <i class="fas fa-check"></i> Valider
                </button>
                <button class="btn btn-secondary btn-sm" onclick="viewMachineDetails('${task.machine_id}')">
                    <i class="fas fa-eye"></i> Voir détails
                </button>
            </td>
        </tr>
    `).join('');
    
    container.innerHTML = tasksHTML;
}

function displayRecentActivities(activities) {
    const container = document.getElementById('recentActivities');
    
    if (activities.length === 0) {
        container.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 20px; color: #6c757d;">
                    <i class="fas fa-history"></i><br>
                    Aucune activité récente
                </td>
            </tr>
        `;
        return;
    }
    
    const activitiesHTML = activities.map(activity => `
        <tr>
            <td>${formatDate(activity.completed_at || activity.created_at)}</td>
            <td>
                <strong>${activity.machine_serial || 'N/A'}</strong><br>
                <small>${activity.machine_type || ''}</small>
            </td>
            <td>${activity.client_name || activity.client_society || 'Client non défini'}</td>
            <td>${activity.stage_label || activity.stage_name}</td>
            <td>
                <span class="status-badge status-${activity.status}">${getStatusText(activity.status)}</span>
            </td>
        </tr>
    `).join('');
    
    container.innerHTML = activitiesHTML;
}

async function validateTask(stageId, machineId) {
    const remarks = prompt('Remarques sur la validation (optionnel):');
    
    try {
        // Use machineId instead of stageId for the new route structure
        const response = await fetch(`${API_BASE_URL}/stages/${machineId}/validate`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                remarks: remarks || ''
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccessMessage(data.message);
            // Reload dashboard data
            loadDashboardData();
        } else {
            showErrorMessage(data.error || 'Erreur lors de la validation');
        }
        
    } catch (error) {
        console.error('Error validating task:', error);
        showErrorMessage('Erreur lors de la validation');
    }
}

function viewMachineDetails(machineId) {
    // Check authentication before navigating
    fetch(`${API_BASE_URL}/users/current`, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(res => res.json())
        .then(data => {
            if (!data.error) {
                window.location.href = `voir-machines.html?machine=${machineId}`;
            } else {
                window.location.href = '../login.html';
            }
        })
        .catch(() => {
            window.location.href = '../login.html';
        });
}

function initializeDashboard() {
    // Initialize navigation
    setupNavigation();
}

function setupNavigation() {
    // My tasks navigation
    const myTasksNav = document.getElementById('nav-my-tasks');
    if (myTasksNav) {
        myTasksNav.addEventListener('click', (e) => {
            e.preventDefault();
            // Scroll to my tasks section
            const tasksSection = document.getElementById('myTasksTable');
            if (tasksSection) {
                tasksSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
}

// Utility functions
function getStatusText(status) {
    const statusMap = {
        'pending': 'En attente',
        'in_progress': 'En cours',
        'completed': 'Terminé'
    };
    return statusMap[status] || status;
}

function getTotalStages() {
    return 5; // Default number of stages
}

function formatDate(dateString) {
    if (!dateString) return 'Date inconnue';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
        return 'Hier';
    } else if (diffDays < 7) {
        return `Il y a ${diffDays} jours`;
    } else {
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }
}

function showLoading() {
    const loadingElements = document.querySelectorAll('.loading-message');
    loadingElements.forEach(el => el.style.display = 'block');
}

function hideLoading() {
    const loadingElements = document.querySelectorAll('.loading-message');
    loadingElements.forEach(el => el.style.display = 'none');
}

function showSuccessMessage(message) {
    // Create and show success toast/modal
    alert('✓ ' + message); // Simple implementation, can be enhanced
}

function showErrorMessage(message) {
    // Create and show error toast/modal
    alert('✗ ' + message); // Simple implementation, can be enhanced
}
