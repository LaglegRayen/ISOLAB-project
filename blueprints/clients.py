"""
Clients CRUD blueprint - Simplified
Handles only Create, Read, Update, Delete operations for clients
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from .firebase_config import get_db, is_firebase_available

# Create clients blueprint
clients_bp = Blueprint('clients', __name__, url_prefix='/api/clients')

@clients_bp.route('', methods=['GET'])
def get_clients():
    """Read - Get all clients"""
    try:
        db = get_db()
        if not is_firebase_available():
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
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        data = request.get_json()
        
        # Basic validation
        required_fields = ['society', 'manager', 'fiscalNumber', 'phone', 'address', 'location']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Prepare client data
        client_data = {
            'society': data['society'],
            'manager': data['manager'],
            'fiscalNumber': data['fiscalNumber'],
            'phone': data['phone'],
            'email': data.get('email', ''),
            'address': data['address'],
            'location': data['location'],
            'type': data.get('type', 'Direct'),
            'status': data.get('status', 'Actif'),
            'paymentMode': data.get('paymentMode', ''),
            'paymentStatus': data.get('paymentStatus', ''),
            'notes': data.get('notes', ''),
            'machines': [],
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        }
        
        # Add to Firestore
        doc_ref = db.collection('clients').add(client_data)
        client_id = doc_ref[1].id
        
        return jsonify({"message": "Client created", "id": client_id}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/<client_id>', methods=['GET'])
def get_client(client_id):
    """Read - Get specific client"""
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
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        data = request.get_json()
        
        doc_ref = db.collection('clients').document(client_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Client not found"}), 404
        
        # Update data
        update_data = {}
        allowed_fields = ['society', 'manager', 'fiscalNumber', 'phone', 'email', 
                         'address', 'location', 'type', 'status', 'paymentMode', 
                         'paymentStatus', 'notes', 'machines']
        
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
