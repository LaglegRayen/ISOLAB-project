"""
Users Blueprint - Updated for Simplified Workflow Structure
Handles user authentication and role-based access with stage assignments
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from datetime import datetime
from .firebase_config import get_db, is_firebase_available
import hashlib

# Create users blueprint
users_bp = Blueprint('users', __name__, url_prefix='/users')

# Frontend URL configuration
FRONTEND_URL = 'https://isolab-support.firebaseapp.com/'

# Define roles for the new simplified structure
ROLES = {
    'admin': 'Administrator',
    'supervisor': 'Supervisor',
    'assembly_tech': 'Assembly Technician',
    'testing_tech': 'Testing Technician',
    'delivery_tech': 'Delivery Technician',
    'installation_tech': 'Installation Technician'
}

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({"error": "Authentication required"}), 401
            
            user_role = session.get('role', '')
            if user_role != required_role and user_role != 'admin':
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@users_bp.route('/', methods=['GET'])
def users_page():
    """Serve the users management page (admin only)"""
    if 'user_id' not in session:
        return redirect(f'{FRONTEND_URL}/login.html')
    
    user_role = session.get('role', '')
    if user_role != 'admin':
        # Redirect non-admin users to dashboard with an error message
        return redirect(f'{FRONTEND_URL}/dashboard.html?error=access_denied')
    
    return redirect(f'{FRONTEND_URL}/users.html')

@users_bp.route('/current', methods=['GET'])
def get_current_user():
    """Get current logged-in user information"""
    try:
        print("DEBUG: /users/current endpoint called")
        print(f"DEBUG: Session data: {dict(session)}")
        print(f"DEBUG: Session has user_id: {'user_id' in session}")
        print(f"DEBUG: User ID value: {session.get('user_id', 'NOT FOUND')}")
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        print(f"DEBUG: Request cookies: {request.cookies}")
        
        if 'user_id' not in session:
            print("DEBUG: No user_id in session - returning 401")
            return jsonify({"error": "Not authenticated"}), 401
        
        db = get_db()
        if not is_firebase_available():
            print("DEBUG: Database not available")
            return jsonify({"error": "Database not available"}), 500
        
        user_id = session['user_id']
        print(f"DEBUG: Looking up user: {user_id}")
        
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            print(f"DEBUG: User {user_id} not found in database")
            session.clear()
            return jsonify({"error": "User not found"}), 404
        
        user_data = user_doc.to_dict()
        
        # Remove sensitive information
        user_data.pop('password', None)
        user_data['id'] = user_id
        
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/all', methods=['GET'])
def get_all_users():
    """Get all users (admin only)"""
    try:
        print("DEBUG: get_all_users endpoint called")
        print(f"DEBUG: Session data: {dict(session)}")
        print(f"DEBUG: User ID: {session.get('user_id')}")
        print(f"DEBUG: User role: {session.get('role')}")
        
        db = get_db()
        if not is_firebase_available():
            print("DEBUG: Database not available")
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in and is admin
        if 'user_id' not in session:
            print("DEBUG: No user_id in session - authentication required")
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('role', '')
        if user_role != 'admin':
            print(f"DEBUG: User role '{user_role}' is not admin - access denied")
            return jsonify({"error": "Admin access required"}), 403
        
        print("DEBUG: Fetching users from database")
        users_ref = db.collection('users')
        users_docs = users_ref.stream()
        
        users = []
        for doc in users_docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            # Remove password from response
            user_data.pop('password', None)
            users.append(user_data)
        
        print(f"DEBUG: Found {len(users)} users")
        return jsonify({"users": users})
        
    except Exception as e:
        print(f"DEBUG: Error in get_all_users: {str(e)}")
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user (admin only or own profile)"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        current_user_id = session.get('user_id')
        user_role = session.get('role', '')
        
        # Allow users to view their own profile or admin to view any
        if user_id != current_user_id and user_role != 'admin':
            return jsonify({"error": "Access denied"}), 403
        
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404
        
        user_data = user_doc.to_dict()
        user_data['id'] = user_id
        # Remove password from response
        user_data.pop('password', None)
        
        return jsonify({"user": user_data})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('', methods=['POST'])
def create_user():
    """Create a new user (admin only)"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in and is admin
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('role', '')
        if user_role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate role
        if data['role'] not in ROLES:
            return jsonify({"error": f"Invalid role. Must be one of: {list(ROLES.keys())}"}), 400
        
        # Check if username or email already exists
        users_ref = db.collection('users')
        
        # Check username
        username_query = users_ref.where('username', '==', data['username']).limit(1)
        if list(username_query.stream()):
            return jsonify({"error": "Username already exists"}), 400
        
        # Check email
        email_query = users_ref.where('email', '==', data['email']).limit(1)
        if list(email_query.stream()):
            return jsonify({"error": "Email already exists"}), 400
        
        # Determine stage access based on role
        stage_access_map = {
            'admin': 'all',
            'supervisor': 'material_collection',
            'assembly_tech': 'assembly',
            'testing_tech': 'testing',
            'delivery_tech': 'delivery',
            'installation_tech': 'installation'
        }
        
        # Create user data
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'password': hash_password(data['password']),
            'role': data['role'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'department': data.get('department', ''),
            'phone': data.get('phone', ''),
            'specialization': data.get('specialization', ''),
            'stage_access': stage_access_map.get(data['role'], 'none'),
            'created_at': datetime.now(),
            'is_active': True,
            'can_validate_all': data['role'] == 'admin'
        }
        
        # Add user to database
        doc_ref = users_ref.add(user_data)
        user_id = doc_ref[1].id
        
        return jsonify({
            "message": "User created successfully",
            "user_id": user_id,
            "username": data['username'],
            "role": data['role'],
            "stage_access": user_data['stage_access']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        current_user_id = session.get('user_id')
        user_role = session.get('role', '')
        
        # Allow users to update their own profile or admin to update any
        if user_id != current_user_id and user_role != 'admin':
            return jsonify({"error": "Access denied"}), 403
        
        data = request.get_json()
        
        # Get user
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404
        
        # Build update data
        update_data = {}
        updatable_fields = ['first_name', 'last_name', 'department', 'phone', 'specialization']
        
        # Admin can update more fields
        if user_role == 'admin':
            updatable_fields.extend(['role', 'is_active', 'stage_access'])
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Handle password update
        if 'password' in data and data['password']:
            update_data['password'] = hash_password(data['password'])
        
        # Update stage_access if role changed (admin only)
        if 'role' in update_data and user_role == 'admin':
            stage_access_map = {
                'admin': 'all',
                'supervisor': 'material_collection',
                'assembly_tech': 'assembly',
                'testing_tech': 'testing',
                'delivery_tech': 'delivery',
                'installation_tech': 'installation'
            }
            update_data['stage_access'] = stage_access_map.get(update_data['role'], 'none')
            update_data['can_validate_all'] = update_data['role'] == 'admin'
        
        if update_data:
            update_data['updated_at'] = datetime.now()
            user_ref.update(update_data)
        
        return jsonify({"message": "User updated successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user (admin only)"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in and is admin
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('role', '')
        if user_role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        current_user_id = session.get('user_id')
        if user_id == current_user_id:
            return jsonify({"error": "Cannot delete your own account"}), 400
        
        # Check if user has assigned machines
        machines_ref = db.collection('machines')
        assigned_machines = machines_ref.where('assigned_user_id', '==', user_id).limit(1)
        if list(assigned_machines.stream()):
            return jsonify({"error": "Cannot delete user with assigned machines"}), 400
        
        # Delete user
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404
        
        user_ref.delete()
        
        return jsonify({"message": "User deleted successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/roles', methods=['GET'])
def get_available_roles():
    """Get available user roles"""
    try:
        # Check if user is logged in and is admin
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('role', '')
        if user_role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        roles_list = []
        for role_key, role_name in ROLES.items():
            roles_list.append({
                'key': role_key,
                'name': role_name,
                'stage_access': {
                    'admin': 'all',
                    'supervisor': 'material_collection',
                    'assembly_tech': 'assembly',
                    'testing_tech': 'testing',
                    'delivery_tech': 'delivery',
                    'installation_tech': 'installation'
                }.get(role_key, 'none')
            })
        
        return jsonify({"roles": roles_list})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/by-stage/<stage_name>', methods=['GET'])
def get_users_by_stage(stage_name):
    """Get users who can access a specific stage"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('role', '')
        if user_role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Get users who can access this stage
        users_ref = db.collection('users')
        
        # Get users with specific stage access or admin users
        stage_users_query = users_ref.where('stage_access', '==', stage_name).where('is_active', '==', True)
        admin_users_query = users_ref.where('stage_access', '==', 'all').where('is_active', '==', True)
        
        stage_users = list(stage_users_query.stream())
        admin_users = list(admin_users_query.stream())
        
        all_users = stage_users + admin_users
        
        users = []
        for doc in all_users:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            # Remove password from response
            user_data.pop('password', None)
            users.append(user_data)
        
        return jsonify({"stage": stage_name, "users": users})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
