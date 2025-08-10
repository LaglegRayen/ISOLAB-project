"""
Stages Blueprint - Updated for Simplified Workflow Structure
Handles machine stages with simple current_stage approach and history tracking
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from .firebase_config import get_db, is_firebase_available
from .users import require_role

# Create stages blueprint
stages_bp = Blueprint('stages', __name__, url_prefix='/stages')

@stages_bp.route('/definitions', methods=['GET'])
def get_stage_definitions():
    """Get all stage definitions with dependencies"""
    try:
        print("DEBUG: Getting stage definitions")
        print(f"DEBUG: User session: {session.get('user_id')}")
        
        db = get_db()
        if not is_firebase_available():
            print("DEBUG: Database not available")
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            print("DEBUG: Authentication required - no user_id in session")
            return jsonify({"error": "Authentication required"}), 401
        
        print("DEBUG: Fetching stages from database")
        stages_ref = db.collection('stages')
        stages_docs = stages_ref.order_by('order').stream()
        
        stages = []
        for doc in stages_docs:
            stage_data = doc.to_dict()
            stage_data['id'] = doc.id
            stages.append(stage_data)
        
        print(f"DEBUG: Found {len(stages)} stages")
        return jsonify({"stages": stages})
        
    except Exception as e:
        print(f"DEBUG: Error getting stage definitions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/machine/<machine_id>/current', methods=['GET'])
def get_machine_current_stage(machine_id):
    """Get current stage information for a specific machine"""
    try:
        print(f"DEBUG: Getting current stage for machine: {machine_id}")
        print(f"DEBUG: User session: {session.get('user_id')}")
        
        db = get_db()
        if not is_firebase_available():
            print("DEBUG: Database not available")
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            print("DEBUG: Authentication required - no user_id in session")
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('role', '')
        user_id = session.get('user_id')
        stage_access = session.get('stage_access', '')
        
        # Get machine
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return jsonify({"error": "Machine not found"}), 404
        
        machine_data = machine_doc.to_dict()
        current_stage = machine_data.get('current_stage')
        assigned_user_id = machine_data.get('assigned_user_id')
        
        # Check access permissions
        if user_role != 'admin':
            if stage_access != current_stage and assigned_user_id != user_id:
                return jsonify({"error": "Access denied to this machine's stage"}), 403
        
        # Get stage definition
        stages_ref = db.collection('stages')
        stage_query = stages_ref.where('name', '==', current_stage).limit(1)
        stage_docs = list(stage_query.stream())
        
        stage_info = None
        if stage_docs:
            stage_info = stage_docs[0].to_dict()
            stage_info['id'] = stage_docs[0].id
        
        return jsonify({
            "machine_id": machine_id,
            "current_stage": current_stage,
            "current_stage_label": machine_data.get('current_stage_label'),
            "assigned_user_id": assigned_user_id,
            "assigned_username": machine_data.get('assigned_username'),
            "stage_started_at": machine_data.get('stage_started_at'),
            "stage_info": stage_info
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/machine/<machine_id>/history', methods=['GET'])
def get_machine_history(machine_id):
    """Get history of completed stages for a machine"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        # Get machine history
        history_ref = db.collection('machine_history')
        history_query = history_ref.where('machine_id', '==', machine_id).order_by('created_at')
        history_docs = history_query.stream()
        
        history = []
        for doc in history_docs:
            history_data = doc.to_dict()
            history_data['id'] = doc.id
            history.append(history_data)
        
        return jsonify({"machine_id": machine_id, "history": history})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/<machine_id>/validate', methods=['POST'])
def validate_machine_stage(machine_id):
    """Validate/complete current stage of a machine and move to next stage"""
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
        username = session.get('username', '')
        
        data = request.get_json()
        remarks = data.get('remarks', '')
        
        # Get machine
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return jsonify({"error": "Machine not found"}), 404
        
        machine_data = machine_doc.to_dict()
        current_stage = machine_data.get('current_stage')
        assigned_user_id = machine_data.get('assigned_user_id')
        
        # Check permissions
        if user_role != 'admin':
            if stage_access != current_stage or assigned_user_id != user_id:
                return jsonify({"error": "Access denied - you are not assigned to this stage"}), 403
        
        # Get current stage definition
        stages_ref = db.collection('stages')
        current_stage_query = stages_ref.where('name', '==', current_stage).limit(1)
        current_stage_docs = list(current_stage_query.stream())
        
        if not current_stage_docs:
            return jsonify({"error": "Current stage definition not found"}), 404
        
        current_stage_def = current_stage_docs[0].to_dict()
        
        # Add completed stage to history
        history_ref = db.collection('machine_history')
        history_entry = {
            'machine_id': machine_id,
            'machine_serial': machine_data.get('serialNumber', 'Unknown'),
            'stage_name': current_stage,
            'stage_label': machine_data.get('current_stage_label', current_stage),
            'status': 'completed',
            'assigned_user_id': user_id,
            'assigned_username': username,
            'started_at': machine_data.get('stage_started_at'),
            'completed_at': datetime.now(),
            'duration_hours': None,  # Calculate if needed
            'remarks': remarks,
            'created_at': datetime.now()
        }
        history_ref.add(history_entry)
        
        # Find next stage
        current_order = current_stage_def.get('order', 0)
        next_stage_query = stages_ref.where('order', '==', current_order + 1).limit(1)
        next_stage_docs = list(next_stage_query.stream())
        
        if next_stage_docs:
            # Move to next stage
            next_stage_def = next_stage_docs[0].to_dict()
            next_stage_name = next_stage_def['name']
            next_stage_label = next_stage_def['label']
            required_role = next_stage_def['required_role']
            
            # Find user for next stage
            users_ref = db.collection('users')
            next_user_query = users_ref.where('role', '==', required_role).where('is_active', '==', True).limit(1)
            next_user_docs = list(next_user_query.stream())
            
            if next_user_docs:
                next_user_data = next_user_docs[0].to_dict()
                next_user_id = next_user_docs[0].id
                next_username = next_user_data.get('username', 'Unknown')
                
                # Update machine to next stage
                machine_ref.update({
                    'current_stage': next_stage_name,
                    'current_stage_label': next_stage_label,
                    'assigned_user_id': next_user_id,
                    'assigned_username': next_username,
                    'stage_started_at': datetime.now(),
                    'updated_at': datetime.now()
                })
                
                message = f"Stage '{current_stage_def.get('label')}' completed. Next stage '{next_stage_label}' assigned to {next_username}."
            else:
                return jsonify({"error": f"No user found for next stage role: {required_role}"}), 500
        else:
            # This was the final stage - mark machine as completed
            machine_ref.update({
                'status': 'Completed',
                'current_stage': None,
                'current_stage_label': 'Completed',
                'assigned_user_id': None,
                'assigned_username': None,
                'completed_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            message = f"Final stage '{current_stage_def.get('label')}' completed. Machine marked as completed."
        
        return jsonify({"message": message})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/my-tasks', methods=['GET'])
def get_my_tasks():
    """Get tasks assigned to current user (machines in their stage)"""
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
        
        # Get machines assigned to this user
        machines_ref = db.collection('machines')
        
        if user_role == 'admin':
            # Admin sees all active machines
            machines_query = machines_ref.where('status', '==', 'En cours')
        else:
            # Regular users see only machines in their stage
            machines_query = machines_ref.where('assigned_user_id', '==', user_id)
        
        machines_docs = machines_query.stream()
        
        my_tasks = []
        for machine_doc in machines_docs:
            machine_data = machine_doc.to_dict()
            machine_id = machine_doc.id
            
            # Skip completed machines for regular users
            if user_role != 'admin' and machine_data.get('status') != 'En cours':
                continue
            
            task = {
                'id': f"{machine_id}_{machine_data.get('current_stage', 'unknown')}",
                'machine_id': machine_id,
                'stage_name': machine_data.get('current_stage'),
                'stage_label': machine_data.get('current_stage_label'),
                'status': 'in_progress',  # All current tasks are in progress
                'machine_info': {
                    'serialNumber': machine_data.get('serialNumber', 'Unknown'),
                    'machineType': machine_data.get('machineType', 'Unknown'),
                    'clientName': machine_data.get('clientName', 'Unknown'),
                    'clientSociety': machine_data.get('clientSociety', 'Unknown')
                },
                'stage_started_at': machine_data.get('stage_started_at'),
                'assigned_username': machine_data.get('assigned_username'),
                'priority': 'normal'
            }
            
            my_tasks.append(task)
        
        return jsonify({"tasks": my_tasks})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data based on user role"""
    try:
        print("DEBUG: Getting dashboard data")
        print(f"DEBUG: User session: {session.get('user_id')}")
        print(f"DEBUG: User role: {session.get('role')}")
        print(f"DEBUG: Stage access: {session.get('stage_access')}")
        
        db = get_db()
        if not is_firebase_available():
            print("DEBUG: Database not available")
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            print("DEBUG: Authentication required - no user_id in session")
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = session.get('user_id')
        user_role = session.get('role', '')
        
        print(f"DEBUG: Fetching dashboard data for user {user_id} with role {user_role}")
        
        dashboard_data = {
            'my_pending_tasks': 0,
            'my_completed_tasks': 0,
            'total_machines': 0,
            'machines_in_my_stages': 0
        }
        
        # Get total machines count
        machines_ref = db.collection('machines')
        all_machines = list(machines_ref.stream())
        dashboard_data['total_machines'] = len(all_machines)
        
        if user_role == 'admin':
            # Admin sees all data
            active_machines = [m for m in all_machines if m.to_dict().get('status') == 'En cours']
            completed_machines = [m for m in all_machines if m.to_dict().get('status') == 'Completed']
            
            dashboard_data['my_pending_tasks'] = len(active_machines)
            dashboard_data['my_completed_tasks'] = len(completed_machines)
            dashboard_data['machines_in_my_stages'] = len(all_machines)
        else:
            # Regular users see only their assigned machines
            my_machines = [m for m in all_machines if m.to_dict().get('assigned_user_id') == user_id]
            my_active_machines = [m for m in my_machines if m.to_dict().get('status') == 'En cours']
            
            dashboard_data['my_pending_tasks'] = len(my_active_machines)
            dashboard_data['machines_in_my_stages'] = len(my_machines)
            
            # Get completed tasks from history
            history_ref = db.collection('machine_history')
            my_history_query = history_ref.where('assigned_user_id', '==', user_id)
            my_history = list(my_history_query.stream())
            dashboard_data['my_completed_tasks'] = len(my_history)
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/recent-activities', methods=['GET'])
def get_recent_activities():
    """Get recent activities from machine history"""
    try:
        db = get_db()
        if not is_firebase_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        user_role = session.get('role', '')
        
        # Get recent activities from machine_history
        history_ref = db.collection('machine_history')
        
        if user_role == 'admin':
            # Admin sees all activities
            query = history_ref.order_by('completed_at', direction='DESCENDING').limit(15)
        else:
            # Regular users see only their activities
            user_id = session.get('user_id')
            # Use simple where clause without order_by to avoid index requirements
            query = history_ref.where('assigned_user_id', '==', user_id)
        
        activities_docs = list(query.stream())
        
        # If not admin, sort in Python and limit
        if user_role != 'admin':
            activities_docs.sort(key=lambda x: x.to_dict().get('completed_at', x.to_dict().get('created_at', datetime.min)), reverse=True)
            activities_docs = activities_docs[:10]
        
        activities = []
        
        # Get machines collection for additional info
        machines_ref = db.collection('machines')
        
        for doc in activities_docs:
            activity_data = doc.to_dict()
            activity_data['id'] = doc.id
            
            # Try to get additional machine info
            machine_id = activity_data.get('machine_id')
            if machine_id:
                try:
                    machine_doc = machines_ref.document(machine_id).get()
                    if machine_doc.exists:
                        machine_data = machine_doc.to_dict()
                        activity_data['machine_type'] = machine_data.get('machineType', '')
                        activity_data['client_name'] = machine_data.get('clientName', '')
                        activity_data['client_society'] = machine_data.get('clientSociety', '')
                except:
                    pass  # Continue without additional machine info
            
            activities.append(activity_data)
        
        return jsonify({"activities": activities})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
