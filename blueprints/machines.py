"""
Machines CRUD blueprint - Enhanced with Role-Based Access
Handles Create, Read, Update, Delete operations for machines with stages
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from .firebase_config import get_db, is_firebase_available
from .users import require_role, create_default_stages_for_machine

# Create machines blueprint
machines_bp = Blueprint('machines', __name__, url_prefix='/machines')

@machines_bp.route('', methods=['GET'])
def get_machines():
    """Read - Get all machines (filtered by user role)"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('user_role')
        user_id = session.get('user_id')
            
        machines_ref = db.collection('machines')
        docs = machines_ref.stream()
        
        machines = []
        for doc in docs:
            machine_data = doc.to_dict()
            machine_data['id'] = doc.id
            
            # For non-admin users, only show machines where they have assigned stages
            if user_role == 'admin':
                machines.append(machine_data)
            else:
                # Check if user has any stages in this machine
                stages_ref = doc.reference.collection('stages')
                user_stages = stages_ref.where('responsible_user_id', '==', user_id).limit(1).get()
                
                if user_stages:
                    machines.append(machine_data)
        
        return jsonify({"machines": machines})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@machines_bp.route('', methods=['POST'])
@require_role(['admin', 'delivery_manager'])  # Only admins and delivery managers can create machines
def create_machine():
    """Create - Add new machine"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        data = request.get_json()
        
        # Basic validation
        required_fields = ['serialNumber', 'machineType', 'clientId']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Verify client exists
        client_ref = db.collection('clients').document(data['clientId'])
        client_doc = client_ref.get()
        if not client_doc.exists:
            return jsonify({"error": "Client not found"}), 404
        
        client_data = client_doc.to_dict()
        
        # Prepare machine data
        machine_data = {
            'serialNumber': data['serialNumber'],
            'machineType': data['machineType'],
            'ficheNumber': data.get('ficheNumber', ''),
            'status': data.get('status', 'En cours'),
            'prixHT': float(data['prixHT']) if data.get('prixHT') else None,
            'prixTTC': float(data['prixTTC']) if data.get('prixTTC') else None,
            'deliveryDate': data.get('deliveryDate', ''),
            'installationDate': data.get('installationDate', ''),
            'deliveredBy': data.get('deliveredBy', ''),
            'installedBy': data.get('installedBy', ''),
            'paymentType': data.get('paymentType', ''),
            'paymentStatus': data.get('paymentStatus', ''),
            'remarques': data.get('remarques', ''),
            'clientId': data['clientId'],
            'clientSociety': client_data.get('society', ''),
            'clientName': client_data.get('manager', ''),
            'clientPhone': client_data.get('phone', ''),
            'created_by': session.get('user_id'),
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        }
        
        # Add to Firestore
        doc_ref = db.collection('machines').add(machine_data)
        machine_id = doc_ref[1].id
        
        # Create default stages for the machine
        stages_created = create_default_stages_for_machine(machine_id)
        if not stages_created:
            print(f"Warning: Could not create default stages for machine {machine_id}")
        
        # Update client's machines list
        current_machines = client_data.get('machines', [])
        if data['serialNumber'] not in current_machines:
            current_machines.append(data['serialNumber'])
            client_ref.update({'machines': current_machines, 'dateUpdated': datetime.now()})
        
        return jsonify({"message": "Machine created with workflow stages", "id": machine_id}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@machines_bp.route('/<machine_id>', methods=['GET'])
def get_machine(machine_id):
    """Read - Get specific machine"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        doc_ref = db.collection('machines').document(machine_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Machine not found"}), 404
        
        machine_data = doc.to_dict()
        machine_data['id'] = doc.id
        
        return jsonify({"machine": machine_data})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@machines_bp.route('/<machine_id>', methods=['PUT'])
def update_machine(machine_id):
    """Update - Modify existing machine"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        data = request.get_json()
        
        doc_ref = db.collection('machines').document(machine_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Machine not found"}), 404
        
        # Update data
        update_data = {}
        allowed_fields = ['machineType', 'ficheNumber', 'status', 'prixHT', 'prixTTC',
                         'deliveryDate', 'installationDate', 'deliveredBy', 'installedBy',
                         'paymentType', 'paymentStatus', 'remarques']
        
        for field in allowed_fields:
            if field in data:
                if field in ['prixHT', 'prixTTC'] and data[field] is not None:
                    update_data[field] = float(data[field])
                else:
                    update_data[field] = data[field]
        
        update_data['dateUpdated'] = datetime.now()
        
        doc_ref.update(update_data)
        
        return jsonify({"message": "Machine updated"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@machines_bp.route('/<machine_id>', methods=['DELETE'])
def delete_machine(machine_id):
    """Delete - Remove machine"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
            
        doc_ref = db.collection('machines').document(machine_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({"error": "Machine not found"}), 404
        
        machine_data = doc.to_dict()
        
        # Remove from client's machines list
        client_ref = db.collection('clients').document(machine_data['clientId'])
        client_doc = client_ref.get()
        
        if client_doc.exists:
            client_data = client_doc.to_dict()
            machines_list = client_data.get('machines', [])
            if machine_data['serialNumber'] in machines_list:
                machines_list.remove(machine_data['serialNumber'])
                client_ref.update({'machines': machines_list, 'dateUpdated': datetime.now()})
        
        doc_ref.delete()
        
        return jsonify({"message": "Machine deleted"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
