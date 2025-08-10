"""
Clients CRUD blueprint - Simplified
Handles only Create, Read, Update, Delete operations for clients
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from datetime import datetime
from .firebase_config import get_db, is_firebase_available

# Create clients blueprint
clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

# Frontend URL configuration
FRONTEND_URL = 'https://isolab-support.firebaseapp.com/'

@clients_bp.route('/', methods=['GET'])
def clients_page():
    if 'user_id' not in session:
        return redirect(f'{FRONTEND_URL}/login.html')
    
    # Check if user is admin
    if session.get('role') != 'admin':
        return redirect(f'{FRONTEND_URL}/dashboard.html')
    
    return redirect(f'{FRONTEND_URL}/clients.html')

@clients_bp.route('/all', methods=['GET'])
def get_clients():
    """Read - Get all clients"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    if session.get('role') != 'admin':
        return jsonify({"error": "Access denied. Admin role required."}), 403
    
    print("Fetching all clients...")
    try:
        db = get_db()
        if not is_firebase_available():
            print("Database not available")
            return jsonify({"error": "Database not available"}), 500
        

        clients_ref = db.collection('clients')
        docs = clients_ref.stream()

        clients = []
        for doc in docs:
            client_data = doc.to_dict()
            client_data['id'] = doc.id
            clients.append(client_data)
        return jsonify({"clients": clients})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('', methods=['POST'])
def create_client():
    """Create - Add new client"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    if session.get('role') != 'admin':
        return jsonify({"error": "Access denied. Admin role required."}), 403
    
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        data = request.get_json()
        print(f"Received client data: {data}")
        
        # Basic validation - match the database structure exactly
        required_fields = ['clientName', 'clientSociety', 'clientPhone', 'clientAddress']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Prepare client data - match database structure exactly
        client_data = {
            'clientName': data['clientName'],
            'clientSociety': data['clientSociety'],
            'clientEmail': data.get('clientEmail', ''),
            'clientPhone': data['clientPhone'],
            'clientAddress': data['clientAddress'],
            'clientLocation': data.get('clientLocation', ''),
            'dateAdded': datetime.now(),
            'created_by': 'admin',  # Should get from session
            'is_active': True
        }
        
        print(f"Saving client data: {client_data}")
        
        # Add to Firestore
        doc_ref = db.collection('clients').add(client_data)
        client_id = doc_ref[1].id
        
        return jsonify({"message": "Client created successfully", "id": client_id}), 201
        
    except Exception as e:
        print(f"Error creating client: {str(e)}")
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/<client_id>', methods=['GET'])
def get_client(client_id):
    """Read - Get specific client"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    if session.get('role') != 'admin':
        return jsonify({"error": "Access denied. Admin role required."}), 403
    
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        doc_ref = db.collection('clients').document(client_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Client not found"}), 404
        
        client_data = doc.to_dict()
        client_data['id'] = doc.id
        
        return jsonify({"client": client_data})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/<client_id>', methods=['PUT'])
def update_client(client_id):
    """Update - Modify existing client"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    if session.get('role') != 'admin':
        return jsonify({"error": "Access denied. Admin role required."}), 403
    
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        data = request.get_json()
        
        doc_ref = db.collection('clients').document(client_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Client not found"}), 404
        
        # Update data - match database structure exactly
        update_data = {}
        allowed_fields = ['clientName', 'clientSociety', 'clientEmail', 'clientPhone', 
                         'clientAddress', 'clientLocation', 'is_active']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        update_data['dateUpdated'] = datetime.now()
        
        doc_ref.update(update_data)
        
        return jsonify({"message": "Client updated"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete - Remove client"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    if session.get('role') != 'admin':
        return jsonify({"error": "Access denied. Admin role required."}), 403
    
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        doc_ref = db.collection('clients').document(client_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Client not found"}), 404
        
        doc_ref.delete()
        
        return jsonify({"message": "Client deleted"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

