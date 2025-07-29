"""
Login Blueprint
Handles login and logout endpoints separately from user management
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from blueprints.firebase_config import get_db, is_firebase_available
from blueprints.users import ROLES

login_bp = Blueprint('login', __name__, url_prefix='/')

@login_bp.route('/login', methods=['POST'])
def login():
    """Simple login - store user ID in session"""
    try:
        db = get_db()
        if not is_firebase_available():
            print("Database not available")
            return jsonify({"error": "Database not available"}), 500
        data = request.get_json()
        email = data.get('email')
        if not email:
            return jsonify({"error": "Email required"}), 400
        # Find user by email
        users_ref = db.collection('users')
        users = users_ref.where('email', '==', email).get()
        if not users:
            print("User not found")
            return jsonify({"error": "User not found"}), 404
        print(f"Found {len(users)} user(s) with email {email}")
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
        print("User logged in successfully")
        return jsonify({
            "message": "Login successful",
            "user": user_data
        })
    except Exception as e:
        print(f"Login failed: {e}") 
        return jsonify({"error": str(e)}), 500
    



# Logout endpoint
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
