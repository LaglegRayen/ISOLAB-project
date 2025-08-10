// API base URL for Google Cloud Run service
// Users management functionality
window.API_BASE_URL = window.API_BASE_URL || 'https://my-service-83716313182.europe-central2.run.app';

// Users page functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded - users.js starting');
    
    // Check authentication
    checkAuthentication();
    
    // Load users data
    console.log('About to call loadUsersData()');
    loadUsersData();
    
    // Initialize search and filters
    initializeSearch();
    
    // Initialize modal
    initializeModal();
    
    console.log('Users page initialization complete');
});ionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded - users.js starting');
    
    // Check authentication and admin role
    checkAuthenticationAndRole();
    
    // Load users data
    console.log('About to call loadUsersData()');
    loadUsersData();
    
    // Initialize search and filters
    initializeSearch();
    
    // Initialize modal
    initializeModal();
    
    console.log('Users page initialization complete');
});

function checkAuthenticationAndRole() {
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
                alert('Accès refusé. Seuls les administrateurs peuvent accéder à cette page.');
                window.location.href = 'https://isolab-support.firebaseapp.com/dashboard.html';
                return;
            }
            
            console.log('Admin user confirmed, proceeding with page load');
        })
        .catch(() => {
            window.location.href = '/login';
        });
}

let allUsers = [];
let selectedUserId = null;

async function loadUsersData() {
    try {
        console.log('Loading users data...');
        
        const response = await fetch(`${API_BASE_URL}/users/all`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Users data received:', data);
            
            allUsers = data.users || [];
            console.log('Total users loaded:', allUsers.length);
            
            displayUsers(allUsers);
            updateUsersCount(allUsers.length);
        } else {
            const errorData = await response.json();
            console.error('Error loading users:', errorData);
            showError('Erreur lors du chargement des utilisateurs: ' + (errorData.error || 'Erreur inconnue'));
        }
    } catch (error) {
        console.error('Error in loadUsersData:', error);
        showError('Erreur de connexion lors du chargement des utilisateurs');
    }
}

function displayUsers(users) {
    const tableBody = document.getElementById('usersTableBody');
    
    if (!users || users.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="no-data">
                    <i class="fas fa-users"></i>
                    <p>Aucun utilisateur trouvé</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = users.map(user => {
        const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'N/A';
        const roleName = getRoleDisplayName(user.role);
        const statusBadge = user.is_active !== false ? 
            '<span class="status-badge status-active">Actif</span>' : 
            '<span class="status-badge status-inactive">Inactif</span>';
        
        return `
            <tr onclick="viewUserDetails('${user.id}')" style="cursor: pointer;">
                <td>${fullName}</td>
                <td>${user.username || 'N/A'}</td>
                <td>${user.email || 'N/A'}</td>
                <td>${roleName}</td>
                <td>${user.department || 'N/A'}</td>
                <td>${user.phone || 'N/A'}</td>
                <td>${statusBadge}</td>
                <td onclick="event.stopPropagation();">
                    <button class="btn-action btn-view" onclick="viewUserDetails('${user.id}')" title="Voir détails">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-action btn-edit" onclick="editUser('${user.id}')" title="Modifier">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action btn-delete" onclick="confirmDeleteUser('${user.id}')" title="Supprimer">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
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
    return roleNames[role] || role || 'N/A';
}

function getStageAccessDisplayName(stageAccess) {
    const stageAccessNames = {
        'all': 'Tous les étapes',
        'material_collection': 'Collecte de matériel',
        'assembly': 'Assemblage',
        'testing': 'Test',
        'delivery': 'Livraison',
        'installation': 'Installation',
        'none': 'Aucun'
    };
    return stageAccessNames[stageAccess] || stageAccess || 'N/A';
}

function updateUsersCount(count) {
    const countElement = document.getElementById('totalUsersCount');
    if (countElement) {
        countElement.textContent = `${count} utilisateur${count !== 1 ? 's' : ''}`;
    }
}

function initializeSearch() {
    const searchInput = document.getElementById('userSearch');
    const roleFilter = document.getElementById('roleFilter');
    const statusFilter = document.getElementById('statusFilter');
    const departmentFilter = document.getElementById('departmentFilter');
    
    // Add event listeners for real-time filtering
    searchInput.addEventListener('input', filterUsers);
    roleFilter.addEventListener('change', filterUsers);
    statusFilter.addEventListener('change', filterUsers);
    departmentFilter.addEventListener('change', filterUsers);
    
    // Allow search on Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchUsers();
        }
    });
}

function filterUsers() {
    const searchTerm = document.getElementById('userSearch').value.toLowerCase();
    const roleFilter = document.getElementById('roleFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const departmentFilter = document.getElementById('departmentFilter').value;
    
    let filteredUsers = allUsers.filter(user => {
        // Search term filter
        const matchesSearch = !searchTerm || 
            (user.first_name && user.first_name.toLowerCase().includes(searchTerm)) ||
            (user.last_name && user.last_name.toLowerCase().includes(searchTerm)) ||
            (user.username && user.username.toLowerCase().includes(searchTerm)) ||
            (user.email && user.email.toLowerCase().includes(searchTerm)) ||
            (user.role && user.role.toLowerCase().includes(searchTerm));
        
        // Role filter
        const matchesRole = !roleFilter || user.role === roleFilter;
        
        // Status filter
        const matchesStatus = !statusFilter || 
            (statusFilter === 'true' && user.is_active !== false) ||
            (statusFilter === 'false' && user.is_active === false);
        
        // Department filter
        const matchesDepartment = !departmentFilter || user.department === departmentFilter;
        
        return matchesSearch && matchesRole && matchesStatus && matchesDepartment;
    });
    
    displayUsers(filteredUsers);
    updateUsersCount(filteredUsers.length);
}

function searchUsers() {
    filterUsers();
}

function initializeModal() {
    // Modal close on outside click
    window.addEventListener('click', function(event) {
        const userModal = document.getElementById('userModal');
        const addUserModal = document.getElementById('addUserModal');
        const editUserModal = document.getElementById('editUserModal');
        
        if (event.target === userModal) {
            closeUserModal();
        }
        if (event.target === addUserModal) {
            closeAddUserModal();
        }
        if (event.target === editUserModal) {
            closeEditUserModal();
        }
    });
}

// User Details Modal Functions
async function viewUserDetails(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const user = data.user;
            
            selectedUserId = userId;
            
            // Populate modal with user data
            document.getElementById('modalUserFullName').textContent = 
                `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'N/A';
            document.getElementById('modalUsername').textContent = user.username || 'N/A';
            document.getElementById('modalUserEmail').textContent = user.email || 'N/A';
            document.getElementById('modalUserRole').textContent = getRoleDisplayName(user.role);
            document.getElementById('modalUserDepartment').textContent = user.department || 'N/A';
            document.getElementById('modalUserPhone').textContent = user.phone || 'N/A';
            document.getElementById('modalUserSpecialization').textContent = user.specialization || 'N/A';
            document.getElementById('modalUserStageAccess').textContent = getStageAccessDisplayName(user.stage_access);
            document.getElementById('modalUserStatus').textContent = 
                user.is_active !== false ? 'Actif' : 'Inactif';
            document.getElementById('modalUserCreatedAt').textContent = 
                user.created_at ? formatDate(user.created_at) : 'N/A';
            
            // Show modal
            document.getElementById('userModal').style.display = 'flex';
        } else {
            const errorData = await response.json();
            alert('Erreur lors du chargement des détails: ' + (errorData.error || 'Erreur inconnue'));
        }
    } catch (error) {
        console.error('Error viewing user details:', error);
        alert('Erreur de connexion lors du chargement des détails');
    }
}

function closeUserModal() {
    document.getElementById('userModal').style.display = 'none';
    selectedUserId = null;
}

function editUser(userId) {
    // Open edit modal with user data
    openEditUserModal(userId);
}

async function openEditUserModal(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const user = data.user;
            
            // Store the user ID for editing
            document.getElementById('editUserModal').setAttribute('data-user-id', userId);
            
            // Populate the form with existing user data
            document.getElementById('editFirstName').value = user.first_name || '';
            document.getElementById('editLastName').value = user.last_name || '';
            document.getElementById('editUsername').value = user.username || '';
            document.getElementById('editEmail').value = user.email || '';
            document.getElementById('editPassword').value = ''; // Always empty for security
            document.getElementById('editRole').value = user.role || '';
            document.getElementById('editIsActive').value = user.is_active !== false ? 'true' : 'false';
            document.getElementById('editDepartment').value = user.department || '';
            document.getElementById('editPhone').value = user.phone || '';
            document.getElementById('editSpecialization').value = user.specialization || '';
            
            // Show the modal
            document.getElementById('editUserModal').style.display = 'flex';
            document.body.style.overflow = 'hidden';
        } else {
            const errorData = await response.json();
            alert('Erreur lors du chargement des données utilisateur: ' + (errorData.error || 'Erreur inconnue'));
        }
    } catch (error) {
        console.error('Error loading user for edit:', error);
        alert('Erreur de connexion lors du chargement des données utilisateur');
    }
}

function closeEditUserModal() {
    document.getElementById('editUserModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    document.getElementById('editUserModal').removeAttribute('data-user-id');
    resetEditUserForm();
}

function resetEditUserForm() {
    document.getElementById('editUserForm').reset();
}

async function submitEditUserForm() {
    const userId = document.getElementById('editUserModal').getAttribute('data-user-id');
    
    if (!userId) {
        alert('Erreur: ID utilisateur manquant');
        return;
    }
    
    // Get form values
    const firstName = document.getElementById('editFirstName').value.trim();
    const lastName = document.getElementById('editLastName').value.trim();
    const password = document.getElementById('editPassword').value; // Don't trim passwords
    const role = document.getElementById('editRole').value;
    const isActive = document.getElementById('editIsActive').value === 'true';
    const department = document.getElementById('editDepartment').value;
    const phone = document.getElementById('editPhone').value.trim();
    const specialization = document.getElementById('editSpecialization').value.trim();
    
    // Validation
    if (!firstName || !lastName || !role) {
        alert('Veuillez remplir tous les champs obligatoires (prénom, nom, rôle)');
        return;
    }
    
    // Password validation (only if provided)
    if (password && password.length < 6) {
        alert('Le mot de passe doit contenir au moins 6 caractères');
        return;
    }
    
    const userData = {
        first_name: firstName,
        last_name: lastName,
        role: role,
        is_active: isActive,
        department: department || '',
        phone: phone || '',
        specialization: specialization || ''
    };
    
    // Only include password if it was provided
    if (password) {
        userData.password = password;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Utilisateur modifié avec succès!');
            closeEditUserModal();
            loadUsersData(); // Refresh the users list
        } else {
            alert('Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    } catch (error) {
        console.error('Error updating user:', error);
        alert('Erreur de connexion lors de la modification de l\'utilisateur');
    }
}

function confirmDeleteUser(userId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ? Cette action est irréversible.')) {
        deleteUserById(userId);
    }
}

async function deleteUserById(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            alert('Utilisateur supprimé avec succès');
            loadUsersData(); // Reload the users list
        } else {
            const errorData = await response.json();
            alert('Erreur lors de la suppression: ' + (errorData.error || 'Erreur inconnue'));
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Erreur de connexion lors de la suppression');
    }
}

// Add User Modal Functions
function openAddUserModal() {
    document.getElementById('addUserModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeAddUserModal() {
    document.getElementById('addUserModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    resetUserForm();
}

function resetUserForm() {
    document.getElementById('addUserForm').reset();
}

async function submitUserForm() {
    // Get form values
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    const department = document.getElementById('department').value;
    const phone = document.getElementById('phone').value.trim();
    const specialization = document.getElementById('specialization').value.trim();
    
    // Validation
    if (!firstName || !lastName || !username || !email || !password || !role) {
        alert('Veuillez remplir tous les champs obligatoires');
        return;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Veuillez entrer une adresse email valide');
        return;
    }
    
    // Password validation
    if (password.length < 6) {
        alert('Le mot de passe doit contenir au moins 6 caractères');
        return;
    }
    
    const userData = {
        first_name: firstName,
        last_name: lastName,
        username: username,
        email: email,
        password: password,
        role: role,
        department: department || '',
        phone: phone || '',
        specialization: specialization || ''
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Utilisateur créé avec succès!');
            closeAddUserModal();
            loadUsersData(); // Refresh the users list
        } else {
            alert('Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    } catch (error) {
        console.error('Error creating user:', error);
        alert('Erreur de connexion lors de la création de l\'utilisateur');
    }
}

// Utility Functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return dateString;
    }
}

function showError(message) {
    const tableBody = document.getElementById('usersTableBody');
    tableBody.innerHTML = `
        <tr>
            <td colspan="8" class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="loadUsersData()">Réessayer</button>
            </td>
        </tr>
    `;
}

// Clear search and filters
function clearFilters() {
    document.getElementById('userSearch').value = '';
    document.getElementById('roleFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('departmentFilter').value = '';
    
    displayUsers(allUsers);
    updateUsersCount(allUsers.length);
}
