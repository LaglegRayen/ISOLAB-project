
"""
Users and Authentication Blueprint
Handles user management, roles, and authentication
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from .firebase_config import get_db, is_firebase_available

# Create users blueprint
users_bp = Blueprint('users', __name__, url_prefix='/users')

# Define role hierarchy and permissions
ROLES = {
    'material_operator': {
        'name': 'Opérateur Matériaux',
        'stages': ['material_collection'],
        'level': 1
    },
    'assembly_technician': {
        'name': 'Technicien Assemblage',
        'stages': ['assembly', 'testing'],
        'level': 2
    },
    'delivery_manager': {
        'name': 'Responsable Livraison',
        'stages': ['delivery', 'installation'],
        'level': 3
    },
    'maintenance_staff': {
        'name': 'Service Maintenance',
        'stages': ['maintenance', 'follow_up'],
        'level': 2
    },
    'admin': {
        'name': 'Administrateur',
        'stages': ['material_collection', 'assembly', 'testing', 'delivery', 'installation', 'maintenance', 'follow_up'],
        'level': 5
    }
}

# Default workflow stages
DEFAULT_STAGES = [
    {
        'name': 'material_collection',
        'label': 'Collecte des matériaux',
        'role': 'material_operator',
        'order': 1,
        'status': 'pending'
    },
    {
        'name': 'assembly',
        'label': 'Assemblage',
        'role': 'assembly_technician',
        'order': 2,
        'status': 'pending'
    },
    {
        'name': 'testing',
        'label': 'Tests et contrôle qualité',
        'role': 'assembly_technician',
        'order': 3,
        'status': 'pending'
    },
    {
        'name': 'delivery',
        'label': 'Livraison',
        'role': 'delivery_manager',
        'order': 4,
        'status': 'pending'
    },
    {
        'name': 'installation',
        'label': 'Installation',
        'role': 'delivery_manager',
        'order': 5,
        'status': 'pending'
    }
]

@users_bp.route('', methods=['GET'])
def get_users():
    """Read - Get all users"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        users_ref = db.collection('users')
        docs = users_ref.stream()
        
        users = []
        for doc in docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            # Add role info
            if user_data.get('role') in ROLES:
                user_data['role_info'] = ROLES[user_data['role']]
            users.append(user_data)
        
        return jsonify({"users": users})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('', methods=['POST'])
def create_user():
    """Create - Add new user"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        data = request.get_json()
        
        # Basic validation
        required_fields = ['name', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate role
        if data['role'] not in ROLES:
            return jsonify({"error": f"Invalid role. Must be one of: {list(ROLES.keys())}"}), 400
        
        # Check if email already exists
        users_ref = db.collection('users')
        existing_user = users_ref.where('email', '==', data['email']).get()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 409
        
        # Prepare user data
        user_data = {
            'name': data['name'],
            'email': data['email'],
            'role': data['role'],
            'status': data.get('status', 'active'),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Add to Firestore
        doc_ref = db.collection('users').add(user_data)
        user_id = doc_ref[1].id
        
        return jsonify({"message": "User created", "id": user_id}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """Read - Get specific user"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "User not found"}), 404
        
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        
        # Add role info
        if user_data.get('role') in ROLES:
            user_data['role_info'] = ROLES[user_data['role']]
        
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update - Modify user"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        
        # Validate role if provided
        if 'role' in data and data['role'] not in ROLES:
            return jsonify({"error": f"Invalid role. Must be one of: {list(ROLES.keys())}"}), 400
        
        # Update fields
        update_data = {}
        for field in ['name', 'email', 'role', 'status']:
            if field in data:
                update_data[field] = data[field]
        
        update_data['updated_at'] = datetime.now()
        
        doc_ref.update(update_data)
        
        return jsonify({"message": "User updated"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete - Remove user"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "User not found"}), 404
        
        doc_ref.delete()
        
        return jsonify({"message": "User deleted"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/login', methods=['POST'])
def login():
    """Simple login - store user ID in session"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email required"}), 400
        
        # Find user by email
        users_ref = db.collection('users')
        users = users_ref.where('email', '==', email).get()
        
        if not users:
            return jsonify({"error": "User not found"}), 404
        
        user_doc = users[0]
        user_data = user_doc.to_dict()
        user_data['id'] = user_doc.id
        
        # Store in session
        session['user_id'] = user_doc.id
        session['user_role'] = user_data['role']
        session['user_name'] = user_data['name']
        
        # Add role info
        if user_data.get('role') in ROLES:
            user_data['role_info'] = ROLES[user_data['role']]
        
        return jsonify({
            "message": "Login successful",
            "user": user_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @users_bp.route('/logout', methods=['POST'])
# def logout():
#     """Logout - clear session"""
#     session.clear()
#     return jsonify({"message": "Logout successful"})

@users_bp.route('/current', methods=['GET'])
def get_current_user():
    """Get current logged in user"""
    try:
        
        if 'user_id' not in session:
            print("User not logged in")
            return jsonify({"error": "Not logged in"}), 401
        
        db = get_db()
        if not is_firebase_available():
            print("Database not available")
            return jsonify({"error": "Database not available"}), 500
            
        doc_ref = db.collection('users').document(session['user_id'])
        doc = doc_ref.get()
        
        if not doc.exists:
            print("User not found in database")
            session.clear()
            return jsonify({"error": "User not found"}), 404
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        
        # Add role info
        if user_data.get('role') in ROLES:
            user_data['role_info'] = ROLES[user_data['role']]
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/roles', methods=['GET'])
def get_roles():
    """Get all available roles"""
    return jsonify({"roles": ROLES})

def require_role(allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_role' not in session:
                return jsonify({"error": "Authentication required"}), 401
            
            if session['user_role'] not in allowed_roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def get_users_by_role(role):
    """Helper function to get users by role"""
    try:
        db = get_db()
        if not is_firebase_available():
            return []
            
        users_ref = db.collection('users')
        users = users_ref.where('role', '==', role).where('status', '==', 'active').get()
        
        return [{'id': doc.id, **doc.to_dict()} for doc in users]
        
    except Exception as e:
        print(f"Error getting users by role: {e}")
        return []

def create_default_stages_for_machine(machine_id):
    """Create default stages for a machine"""
    try:
        db = get_db()
        if not is_firebase_available():
            return False
            
        # Get machine document
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return False
        
        # Create stages subcollection
        stages_ref = machine_ref.collection('stages')
        
        for stage_template in DEFAULT_STAGES:
            # Get users with this role
            role_users = get_users_by_role(stage_template['role'])
            
            if role_users:
                # Randomly assign a user with the matching role
                import random
                assigned_user = random.choice(role_users)
                responsible_user_id = assigned_user['id']
            else:
                responsible_user_id = None
            
            stage_data = {
                'name': stage_template['name'],
                'label': stage_template['label'],
                'role': stage_template['role'],
                'order': stage_template['order'],
                'status': 'in_progress' if stage_template['order'] == 1 else 'pending',
                'responsible_user_id': responsible_user_id,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            stages_ref.add(stage_data)
        
        return True
        
    except Exception as e:
        print(f"Error creating default stages: {e}")
        return False
