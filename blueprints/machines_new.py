"""
Machines CRUD Blueprint - Updated for Simplified Workflow Structure
Handles machine operations with simple current_stage approach
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect
from datetime import datetime
from .firebase_config import get_db, is_firebase_available
from .users import require_role

# Create machines blueprint
machines_bp = Blueprint('machines', __name__, url_prefix='/machines')

# Frontend URL configuration
FRONTEND_URL = 'https://isolab-support.firebaseapp.com'

@machines_bp.route('/view', methods=['GET'])
def view_machines():
    """Redirect to the machines view page on frontend"""
    return redirect(f'{FRONTEND_URL}/voir-machines.html')

@machines_bp.route('', methods=['GET'])
def get_all_machines():
    """Get all machines filtered by user role and stage access"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = session.get('user_id')
        user_role = session.get('role', '')
        stage_access = session.get('stage_access', '')
        
        machines_ref = db.collection('machines')
        
        if user_role == 'admin':
            # Admin sees all machines
            machines_docs = machines_ref.stream()
        else:
            # Regular users see machines in their stage or assigned to them
            machines_docs = []
            
            # Get machines in user's accessible stage
            if stage_access and stage_access != 'all':
                stage_machines = machines_ref.where('current_stage', '==', stage_access).stream()
                machines_docs.extend(stage_machines)
            
            # Also get machines directly assigned to this user
            assigned_machines = machines_ref.where('assigned_user_id', '==', user_id).stream()
            machines_docs.extend(assigned_machines)
        
        machines = []
        seen_ids = set()  # Avoid duplicates
        
        for doc in machines_docs:
            if doc.id in seen_ids:
                continue
            seen_ids.add(doc.id)
            
            machine_data = doc.to_dict()
            machine_data['id'] = doc.id
            
            # Add current stage information
            current_stage = machine_data.get('current_stage')
            if current_stage:
                # Get stage definition for additional info
                stages_ref = db.collection('stages')
                stage_query = stages_ref.where('name', '==', current_stage).limit(1)
                stage_docs = list(stage_query.stream())
                
                if stage_docs:
                    stage_def = stage_docs[0].to_dict()
                    machine_data['stage_info'] = {
                        'order': stage_def.get('order'),
                        'estimated_duration_hours': stage_def.get('estimated_duration_hours'),
                        'required_role': stage_def.get('required_role')
                    }
            
            machines.append(machine_data)
        
        return jsonify({"data": machines})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@machines_bp.route('/<machine_id>', methods=['GET'])
def get_machine(machine_id):
    """Get specific machine details with history"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = session.get('user_id')
        user_role = session.get('role', '')
        stage_access = session.get('stage_access', '')
        
        # Get machine
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return jsonify({"error": "Machine not found"}), 404
        
        machine_data = machine_doc.to_dict()
        machine_data['id'] = machine_id
        
        # Check access permissions
        if user_role != 'admin':
            current_stage = machine_data.get('current_stage')
            assigned_user_id = machine_data.get('assigned_user_id')
            
            if stage_access != current_stage and assigned_user_id != user_id:
                return jsonify({"error": "Access denied to this machine"}), 403
        
        # Get machine history
        history_ref = db.collection('machine_history')
        history_query = history_ref.where('machine_id', '==', machine_id).order_by('created_at')
        history_docs = history_query.stream()
        
        history = []
        for doc in history_docs:
            history_data = doc.to_dict()
            history_data['id'] = doc.id
            history.append(history_data)
        
        machine_data['history'] = history
        
        # Get current stage definition
        current_stage = machine_data.get('current_stage')
        if current_stage:
            stages_ref = db.collection('stages')
            stage_query = stages_ref.where('name', '==', current_stage).limit(1)
            stage_docs = list(stage_query.stream())
            
            if stage_docs:
                stage_def = stage_docs[0].to_dict()
                machine_data['current_stage_info'] = stage_def
        
        return jsonify({"machine": machine_data})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@machines_bp.route('', methods=['POST'])
def create_machine():
    """Create a new machine"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in and has admin role
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('role', '')
        if user_role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        data = request.get_json()
        
        # Get first stage (material_collection) and assign to supervisor
        stages_ref = db.collection('stages')
        first_stage_query = stages_ref.where('order', '==', 1).limit(1)
        first_stage_docs = list(first_stage_query.stream())
        
        if not first_stage_docs:
            return jsonify({"error": "No stages defined"}), 500
        
        first_stage_def = first_stage_docs[0].to_dict()
        first_stage_name = first_stage_def['name']
        first_stage_label = first_stage_def['label']
        required_role = first_stage_def['required_role']
        
        # Find user for first stage
        users_ref = db.collection('users')
        first_user_query = users_ref.where('role', '==', required_role).where('is_active', '==', True).limit(1)
        first_user_docs = list(first_user_query.stream())
        
        if not first_user_docs:
            return jsonify({"error": f"No user found for stage role: {required_role}"}), 500
        
        first_user_data = first_user_docs[0].to_dict()
        first_user_id = first_user_docs[0].id
        first_username = first_user_data.get('username', 'Unknown')
        
        # Create machine data
        machine_data = {
            'serialNumber': data.get('serialNumber'),
            'ficheNumber': data.get('ficheNumber'),
            'machineType': data.get('machineType'),
            'clientId': data.get('clientId'),
            'clientName': data.get('clientName'),
            'clientSociety': data.get('clientSociety'),
            'status': 'En cours',
            'current_stage': first_stage_name,
            'current_stage_label': first_stage_label,
            'assigned_user_id': first_user_id,
            'assigned_username': first_username,
            'stage_started_at': datetime.now(),
            'prixHT': data.get('prixHT', 0),
            'prixTTC': data.get('prixTTC', 0),
            'paymentStatus': data.get('paymentStatus', 'En cours'),
            'paymentType': data.get('paymentType', 'Crédit'),
            'facturation': data.get('facturation', 'Non facturée'),
            'confirmation': data.get('confirmation', 'En attente'),
            'remarques': data.get('remarques', ''),
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'created_by': session.get('username', 'Unknown'),
            'updated_at': datetime.now()
        }
        
        # Add machine to database
        machines_ref = db.collection('machines')
        doc_ref = machines_ref.add(machine_data)
        machine_id = doc_ref[1].id
        
        return jsonify({
            "message": "Machine created successfully",
            "machine_id": machine_id,
            "assigned_to": first_username,
            "current_stage": first_stage_label
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@machines_bp.route('/<machine_id>', methods=['PUT'])
def update_machine(machine_id):
    """Update machine information"""
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
        
        data = request.get_json()
        
        # Get machine
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return jsonify({"error": "Machine not found"}), 404
        
        # Update allowed fields (not workflow-related fields)
        update_data = {}
        updatable_fields = [
            'serialNumber', 'ficheNumber', 'machineType', 'clientId', 
            'clientName', 'clientSociety', 'prixHT', 'prixTTC',
            'paymentStatus', 'paymentType', 'facturation', 'confirmation', 'remarques'
        ]
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            update_data['dateUpdated'] = datetime.now()
            update_data['updated_at'] = datetime.now()
            machine_ref.update(update_data)
        
        return jsonify({"message": "Machine updated successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@machines_bp.route('/<machine_id>', methods=['DELETE'])
def delete_machine(machine_id):
    """Delete a machine and its history"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in and has admin role
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('role', '')
        if user_role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Delete machine
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return jsonify({"error": "Machine not found"}), 404
        
        machine_ref.delete()
        
        # Delete machine history
        history_ref = db.collection('machine_history')
        history_query = history_ref.where('machine_id', '==', machine_id)
        history_docs = history_query.stream()
        
        deleted_history = 0
        for doc in history_docs:
            doc.reference.delete()
            deleted_history += 1
        
        return jsonify({
            "message": "Machine and history deleted successfully",
            "deleted_history_entries": deleted_history
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@machines_bp.route('/statistics', methods=['GET'])
def get_machines_statistics():
    """Get machine statistics by stage"""
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
        
        # Get all machines
        machines_ref = db.collection('machines')
        machines_docs = machines_ref.stream()
        
        # Count by stage
        stage_counts = {}
        total_machines = 0
        completed_machines = 0
        
        for doc in machines_docs:
            machine_data = doc.to_dict()
            current_stage = machine_data.get('current_stage', 'unknown')
            status = machine_data.get('status', 'En cours')
            
            if status == 'Completed':
                completed_machines += 1
                current_stage = 'completed'
            
            if current_stage not in stage_counts:
                stage_counts[current_stage] = 0
            stage_counts[current_stage] += 1
            total_machines += 1
        
        # Get stage definitions for labels
        stages_ref = db.collection('stages')
        stages_docs = stages_ref.stream()
        
        stage_labels = {}
        for doc in stages_docs:
            stage_data = doc.to_dict()
            stage_labels[stage_data['name']] = stage_data['label']
        
        # Format statistics
        formatted_stats = []
        for stage_name, count in stage_counts.items():
            formatted_stats.append({
                'stage': stage_name,
                'label': stage_labels.get(stage_name, stage_name.title()),
                'count': count,
                'percentage': round((count / total_machines) * 100, 1) if total_machines > 0 else 0
            })
        
        return jsonify({
            "total_machines": total_machines,
            "completed_machines": completed_machines,
            "active_machines": total_machines - completed_machines,
            "stage_distribution": formatted_stats
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
