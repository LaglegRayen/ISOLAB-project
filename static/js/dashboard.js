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
    fetch('/users/current')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                window.location.href = '../login.html';
            } else {
                displayUserInfo(data);
                configureNavigationByRole(data.role);
            }
        })
        .catch(() => {
            window.location.href = '../login.html';
        });
}

function displayUserInfo(user) {
    const userInfo = document.getElementById('userInfo');
    const roleName = user.role_info ? user.role_info.name : user.role;
    userInfo.textContent = `${user.name} - ${roleName}`;
}

function configureNavigationByRole(userRole) {
    const adminOnlyItems = ['nav-users-item', 'nav-add-client-item'];
    const deliveryManagerItems = ['nav-add-machine-item'];
    
    // Hide admin-only items for non-admin users
    if (userRole !== 'admin') {
        adminOnlyItems.forEach(itemId => {
            const item = document.getElementById(itemId);
            if (item) item.style.display = 'none';
        });
    }
    
    // Hide delivery manager items for non-delivery managers and non-admins
    if (userRole !== 'admin' && userRole !== 'delivery_manager') {
        deliveryManagerItems.forEach(itemId => {
            const item = document.getElementById(itemId);
            if (item) item.style.display = 'none';
        });
    }
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
        const response = await fetch('/stages/dashboard');
        
        if (!response.ok) {
            throw new Error('Failed to load dashboard stats');
        }
        
        const data = await response.json();
        
        // Update stat cards
        document.getElementById('myPendingTasks').textContent = data.my_pending_tasks || 0;
        document.getElementById('myCompletedTasks').textContent = data.my_completed_tasks || 0;
        document.getElementById('machinesInMyStages').textContent = data.machines_in_my_stages || 0;
        document.getElementById('totalMachines').textContent = data.total_machines || 0;
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        // Set default values
        document.getElementById('myPendingTasks').textContent = '0';
        document.getElementById('myCompletedTasks').textContent = '0';
        document.getElementById('machinesInMyStages').textContent = '0';
        document.getElementById('totalMachines').textContent = '0';
    }
}

async function loadMyTasks() {
    try {
        const response = await fetch('/stages/my-tasks');
        
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
        const response = await fetch('/stages/recent-activities');
        
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
        const response = await fetch(`/stages/${machineId}/validate`, {
            method: 'POST',
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
    fetch('/users/current')
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
