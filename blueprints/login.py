"""
Login Blueprint - Updated for Simplified Workflow Structure
Handles login and logout with new role and stage_access structure
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from blueprints.firebase_config import get_db, is_firebase_available
from google.cloud.firestore_v1.base_query import FieldFilter
import hashlib

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

login_bp = Blueprint('login', __name__, url_prefix='/')

@login_bp.route('/login', methods=['POST'])
def login():
    """Login with username/email and password"""
    try:
        db = get_db()
        if not is_firebase_available():
            print("Database not available")
            return jsonify({"error": "Database not available"}), 500
        print("✅ Firebase connection established")
        
        data = request.get_json()
        identifier = data.get('email') or data.get('username')  # Support both email and username
        password = data.get('password')
        
        if not identifier:
            return jsonify({"error": "Email or username required"}), 400
        
        if not password:
            return jsonify({"error": "Password required"}), 400
        
        # Find user by email or username
        users_ref = db.collection('users')
        
        # Try to find by email first
        users = users_ref.where(filter=FieldFilter("email", "==", identifier)).get()
        
        # If not found by email, try username
        if not users:
            users = users_ref.where(filter=FieldFilter("username", "==", identifier)).get()
        
        if not users:
            print(f"User not found: {identifier}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        user_doc = users[0]
        user_data = user_doc.to_dict()
        user_data['id'] = user_doc.id
        
        # Simple password verification using hash
        hashed_input = hash_password(password)
        if user_data.get('password') != hashed_input:
            print(f"Invalid password for user: {identifier}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check if user is active
        if not user_data.get('is_active', True):
            return jsonify({"error": "Account is deactivated"}), 403
        
        # Store in session with new structure
        session['user_id'] = user_doc.id
        session['role'] = user_data['role']  # Changed from user_role to role
        session['username'] = user_data.get('username', 'Unknown')
        session['stage_access'] = user_data.get('stage_access', 'none')
        session['first_name'] = user_data.get('first_name', 'Unknown')
        session['last_name'] = user_data.get('last_name', 'User')
        
        print(f"✅ User logged in: {user_data.get('username')} ({user_data['role']}) - Stage access: {user_data.get('stage_access')}")
        
        # Remove password from response
        user_data.pop('password', None)
        
        return jsonify({
            "message": "Login successful",
            "user": user_data
        })
        
    except Exception as e:
        print(f"Login failed: {e}") 
        return jsonify({"error": str(e)}), 500

@login_bp.route('/logout', methods=['POST'])
def logout():
    """Logout - clear session"""
    session.clear()
    return jsonify({"message": "Logout successful"})




# @login_bp.route('/signup', methods=['POST'])
# def signup():
#     """User registration endpoint"""
#     try:
#         db = get_db()
#         if not is_firebase_available():
#             return jsonify({"error": "Database not available"}), 500
        
#         data = request.get_json()
#         required_fields = ['name', 'email', 'role', 'password']
#         for field in required_fields:
#             if not data.get(field):
#                 return jsonify({"error": f"Missing required field: {field}"}), 400
#         # Validate role
#         if data['role'] not in ROLES:
#             return jsonify({"error": f"Invalid role. Must be one of: {list(ROLES.keys())}"}), 400
#         # Check if email already exists
#         users_ref = db.collection('users')
#         existing_user = users_ref.where('email', '==', data['email']).get()
#         if existing_user:
#             return jsonify({"error": "User with this email already exists"}), 409
#         # Prepare user data


#         user_data = {
#             'name': data['name'],
#             'email': data['email'],
#             'role': data['role'],
#             'password': data['password'],
#             'status': data.get('status', 'active'),
#             'created_at': datetime.now(),
#             'updated_at': datetime.now()
#         }
#         # Add to Firestore
#         doc_ref = db.collection('users').add(user_data)
#         user_id = doc_ref[1].id
#         return jsonify({"message": "Signup successful", "id": user_id}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
