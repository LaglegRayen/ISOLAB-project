"""
Stages Blueprint
Handles machine workflow stages and their validation
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from .firebase_config import get_db, is_firebase_available
from .users import ROLES, require_role

# Create stages blueprint
stages_bp = Blueprint('stages', __name__, url_prefix='/stages')

@stages_bp.route('/machine/<machine_id>', methods=['GET'])
def get_machine_stages(machine_id):
    """Get all stages for a specific machine"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('user_role')
        user_id = session.get('user_id')
        
        # Get machine
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return jsonify({"error": "Machine not found"}), 404
        
        # Get stages
        stages_ref = machine_ref.collection('stages')
        stages_docs = stages_ref.order_by('order').stream()
        
        stages = []
        for doc in stages_docs:
            stage_data = doc.to_dict()
            stage_data['id'] = doc.id
            
            # Filter based on user role (admins see all)
            if user_role == 'admin' or stage_data.get('role') == user_role or stage_data.get('responsible_user_id') == user_id:
                stages.append(stage_data)
        
        return jsonify({"stages": stages})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/<stage_id>/validate', methods=['POST'])
def validate_stage(stage_id):
    """Validate/complete a stage"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = session.get('user_id')
        user_role = session.get('user_role')
        
        data = request.get_json()
        
        # Find the stage across all machines (we need the machine_id)
        # This is a bit complex with Firestore, so we'll get it from the request
        machine_id = data.get('machine_id')
        if not machine_id:
            return jsonify({"error": "machine_id required"}), 400
        
        # Get the stage
        machine_ref = db.collection('machines').document(machine_id)
        stage_ref = machine_ref.collection('stages').document(stage_id)
        stage_doc = stage_ref.get()
        
        if not stage_doc.exists:
            return jsonify({"error": "Stage not found"}), 404
        
        stage_data = stage_doc.to_dict()
        
        # Check permissions
        if user_role != 'admin' and stage_data.get('responsible_user_id') != user_id:
            return jsonify({"error": "You are not authorized to validate this stage"}), 403
        
        # Check if stage is in correct status
        if stage_data.get('status') != 'in_progress':
            return jsonify({"error": "Stage is not in progress"}), 400
        
        # Update stage to completed
        stage_ref.update({
            'status': 'completed',
            'completed_at': datetime.now(),
            'completed_by': user_id,
            'updated_at': datetime.now(),
            'remarks': data.get('remarks', '')
        })
        
        # Get all stages to check workflow
        stages_ref = machine_ref.collection('stages')
        all_stages = list(stages_ref.order_by('order').stream())
        
        current_stage_order = stage_data.get('order', 0)
        
        # Find next stage
        next_stage = None
        for stage_doc in all_stages:
            stage_info = stage_doc.to_dict()
            if stage_info.get('order', 0) == current_stage_order + 1:
                next_stage = {'id': stage_doc.id, **stage_info}
                break
        
        if next_stage:
            # Activate next stage
            next_stage_ref = machine_ref.collection('stages').document(next_stage['id'])
            next_stage_ref.update({
                'status': 'in_progress',
                'started_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            message = f"Stage validated. Next stage '{next_stage['label']}' is now in progress."
        else:
            # This was the last stage - mark machine as completed
            machine_ref.update({
                'status': 'Completed',
                'completed_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            message = "Final stage validated. Machine marked as completed."
        
        return jsonify({"message": message})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/my-tasks', methods=['GET'])
def get_my_tasks():
    """Get tasks assigned to current user"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = session.get('user_id')
        user_role = session.get('user_role')
        
        # Get all machines
        machines_ref = db.collection('machines')
        machines_docs = machines_ref.stream()
        
        my_tasks = []
        
        for machine_doc in machines_docs:
            machine_data = machine_doc.to_dict()
            machine_id = machine_doc.id
            
            # Get stages for this machine
            stages_ref = machine_doc.reference.collection('stages')
            
            if user_role == 'admin':
                # Admins see all in-progress stages
                stages_docs = stages_ref.where('status', '==', 'in_progress').stream()
            else:
                # Users see only their assigned stages that are in progress
                stages_docs = stages_ref.where('responsible_user_id', '==', user_id).where('status', '==', 'in_progress').stream()
            
            for stage_doc in stages_docs:
                stage_data = stage_doc.to_dict()
                stage_data['id'] = stage_doc.id
                stage_data['machine_id'] = machine_id
                stage_data['machine_info'] = {
                    'serialNumber': machine_data.get('serialNumber'),
                    'machineType': machine_data.get('machineType'),
                    'clientSociety': machine_data.get('clientSociety')
                }
                my_tasks.append(stage_data)
        
        return jsonify({"tasks": my_tasks})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data based on user role"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = session.get('user_id')
        user_role = session.get('user_role')
        
        dashboard_data = {
            'my_pending_tasks': 0,
            'my_completed_tasks': 0,
            'total_machines': 0,
            'machines_in_my_stages': 0
        }
        
        # Get all machines
        machines_ref = db.collection('machines')
        machines_docs = list(machines_ref.stream())
        dashboard_data['total_machines'] = len(machines_docs)
        
        machines_with_my_stages = set()
        
        for machine_doc in machines_docs:
            machine_id = machine_doc.id
            
            # Get stages for this machine
            stages_ref = machine_doc.reference.collection('stages')
            
            if user_role == 'admin':
                # Admin sees all stages
                pending_stages = list(stages_ref.where('status', '==', 'in_progress').stream())
                completed_stages = list(stages_ref.where('status', '==', 'completed').stream())
                
                dashboard_data['my_pending_tasks'] += len(pending_stages)
                dashboard_data['my_completed_tasks'] += len(completed_stages)
                
                if pending_stages or completed_stages:
                    machines_with_my_stages.add(machine_id)
            else:
                # User sees only their assigned stages
                my_pending = list(stages_ref.where('responsible_user_id', '==', user_id).where('status', '==', 'in_progress').stream())
                my_completed = list(stages_ref.where('responsible_user_id', '==', user_id).where('status', '==', 'completed').stream())
                
                dashboard_data['my_pending_tasks'] += len(my_pending)
                dashboard_data['my_completed_tasks'] += len(my_completed)
                
                if my_pending or my_completed:
                    machines_with_my_stages.add(machine_id)
        
        dashboard_data['machines_in_my_stages'] = len(machines_with_my_stages)
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
