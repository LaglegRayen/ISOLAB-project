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
        print("DEBUG: Login endpoint called")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request content type: {request.content_type}")

        db = get_db()
        if not is_firebase_available():
            print("DEBUG: Database not available")
            return jsonify({"error": "Database not available"}), 500
        print("DEBUG: Firebase connection established")
        
        data = request.get_json()
        print(f"DEBUG: Received data: {data}")
        
        identifier = data.get('email') or data.get('username')  # Support both email and username
        password = data.get('password')

        print(f"DEBUG: Identifier: {identifier}")
        print(f"DEBUG: Password provided: {'Yes' if password else 'No'}")

        if not identifier:
            print("DEBUG: No identifier provided")
            return jsonify({"error": "Email or username required"}), 400
        
        if not password:
            print("DEBUG: No password provided")
            return jsonify({"error": "Password required"}), 400
        
        # Find user by email or username
        users_ref = db.collection('users')
        print(f"DEBUG: Searching for user by email: {identifier}")
        
        # Try to find by email first
        users = users_ref.where(filter=FieldFilter("email", "==", identifier)).get()
        print(f"DEBUG: Users found by email: {len(users)}")

        # If not found by email, try username
        if not users:
            print(f"DEBUG: Searching for user by username: {identifier}")
            users = users_ref.where(filter=FieldFilter("username", "==", identifier)).get()
            print(f"DEBUG: Users found by username: {len(users)}")
        
        if not users:
            print(f"DEBUG: User not found: {identifier}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        user_doc = users[0]
        user_data = user_doc.to_dict()
        user_data['id'] = user_doc.id
        
        print(f"DEBUG: User found: {user_data.get('email')} (ID: {user_doc.id})")
        print(f"DEBUG: User role: {user_data.get('role')}")
        print(f"DEBUG: User active: {user_data.get('is_active', True)}")
        
        # Simple password verification using hash
        hashed_input = hash_password(password)
        stored_password = user_data.get('password')
        print(f"DEBUG: Password hash match: {hashed_input == stored_password}")
        
        if stored_password != hashed_input:
            print(f"DEBUG: Invalid password for user: {identifier}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check if user is active
        if not user_data.get('is_active', True):
            print(f"DEBUG: Account deactivated for user: {identifier}")
            return jsonify({"error": "Account is deactivated"}), 403
        
        # Store in session with new structure
        session['user_id'] = user_doc.id
        session['role'] = user_data['role']  # Changed from user_role to role
        session['username'] = user_data.get('username', 'Unknown')
        session['stage_access'] = user_data.get('stage_access', 'none')
        session['first_name'] = user_data.get('first_name', 'Unknown')
        session['last_name'] = user_data.get('last_name', 'User')
        
        print(f"DEBUG: Session created for user: {user_data.get('username')} ({user_data['role']})")
        print(f"DEBUG: Session data after setting: {dict(session)}")
        print(f"DEBUG: Session data - User ID: {user_doc.id}")
        print(f"DEBUG: Session data - Role: {user_data['role']}")
        print(f"DEBUG: Session data - Stage access: {user_data.get('stage_access')}")
        
        print(f"User logged in: {user_data.get('username')} ({user_data['role']}) - Stage access: {user_data.get('stage_access')}")
        
        # Remove password from response
        user_data.pop('password', None)
        
        print(f"DEBUG: Login successful, returning user data")
        
        response = jsonify({
            "message": "Login successful",
            "user": user_data
        })
        
        print(f"DEBUG: Response headers: {response.headers}")
        
        return response
        
    except Exception as e:
        print(f"DEBUG: Login failed with exception: {e}") 
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@login_bp.route('/logout', methods=['POST'])
def logout():
    """Logout - clear session"""
    print("DEBUG: Logout endpoint called")
    user_id = session.get('user_id', 'Unknown')
    username = session.get('username', 'Unknown')
    print(f"DEBUG: Logging out user: {username} (ID: {user_id})")
    
    session.clear()
    print("DEBUG: Session cleared successfully")
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
