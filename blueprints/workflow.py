"""
Workflow management blueprint for Flask app
Handles workflow stages, updates, and tracking
"""

from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
from functools import wraps
from .firebase_config import get_db, is_firebase_available

workflow_bp = Blueprint('workflow', __name__)

def login_required(f):
    """Simple login required decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_user_role():
    """Get current user role from session"""
    return session.get('user_role', 'user')

@workflow_bp.route('/workflows', methods=['GET'])
@login_required
def get_workflows():
    """Get all workflows with their current status - filtered by user role"""
    print("DEBUG: Getting workflows")
    print(f"DEBUG: User session: {session.get('user_id')}")
    print(f"DEBUG: User role: {session.get('user_role')}")
    
    if not is_firebase_available():
        print("DEBUG: Database not available")
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        db = get_db()
        user_role = session.get('user_role', '').lower()
        user_id = session.get('user_id')
        
        print(f"DEBUG: Fetching workflows for user {user_id} with role {user_role}")
        
        # Get all machines with their workflow instances
        machines_ref = db.collection('machines')
        machines = machines_ref.stream()
        
        workflows = []
        machine_count = 0
        for machine in machines:
            machine_count += 1
            machine_data = machine.to_dict()
            workflow_instance = machine_data.get('workflow_instance')
            
            if workflow_instance:
                # Admin users see all workflows
                include_workflow = False
                if 'admin' in user_role:
                    include_workflow = True
                else:
                    # Non-admin users only see workflows where they are assigned to stages
                    stages = workflow_instance.get('stages', [])
                    for stage in stages:
                        assigned_users = stage.get('assigned_users', [])
                        if any(user.get('user_id') == user_id for user in assigned_users):
                            include_workflow = True
                            break
                
                if include_workflow:
                    workflow_summary = {
                        'machine_id': machine.id,
                        'serial_number': machine_data.get('serialNumber', 'Unknown'),
                        'machine_type': machine_data.get('machineType', 'Unknown'),
                        'client_society': machine_data.get('clientSociety', 'Unknown'),
                        'workflow_status': machine_data.get('workflow_status', 'Unknown'),
                        'current_stage': machine_data.get('current_stage', 'Unknown'),
                        'stages': workflow_instance.get('stages', []),
                        'created_at': workflow_instance.get('created_at'),
                        'updated_at': workflow_instance.get('updated_at')
                    }
                    workflows.append(workflow_summary)
        
        return jsonify({
            'success': True,
            'workflows': workflows,
            'total': len(workflows)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching workflows: {str(e)}'}), 500

@workflow_bp.route('/workflows/<machine_id>', methods=['GET'])
@login_required
def get_machine_workflow(machine_id):
    """Get detailed workflow for a specific machine - with role-based access"""
    if not is_firebase_available():
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        db = get_db()
        user_role = session.get('user_role', '').lower()
        user_id = session.get('user_id')
        
        # Get machine document
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return jsonify({'error': 'Machine not found'}), 404
        
        machine_data = machine_doc.to_dict()
        workflow_instance = machine_data.get('workflow_instance')
        
        if not workflow_instance:
            return jsonify({'error': 'No workflow found for this machine'}), 404
        
        # Check if user has access to this machine
        if 'admin' not in user_role:
            # Non-admin users can only access machines where they are assigned to stages
            stages = workflow_instance.get('stages', [])
            user_has_access = False
            for stage in stages:
                assigned_users = stage.get('assigned_users', [])
                if any(user.get('user_id') == user_id for user in assigned_users):
                    user_has_access = True
                    break
            
            if not user_has_access:
                return jsonify({'error': 'Access denied - you are not assigned to this machine'}), 403
        
        # Add machine info to workflow
        workflow_instance['machine_info'] = {
            'id': machine_id,
            'serial_number': machine_data.get('serialNumber', 'Unknown'),
            'machine_type': machine_data.get('machineType', 'Unknown'),
            'client_society': machine_data.get('clientSociety', 'Unknown'),
            'status': machine_data.get('status', 'Unknown')
        }
        
        return jsonify({
            'success': True,
            'workflow': workflow_instance
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching workflow: {str(e)}'}), 500

@workflow_bp.route('/workflows/<machine_id>/stage/<stage_name>', methods=['PUT'])
@login_required
def update_workflow_stage(machine_id, stage_name):
    """Update a specific workflow stage - with role-based access control"""
    if not is_firebase_available():
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        if new_status not in ['pending', 'in_progress', 'completed', 'blocked']:
            return jsonify({'error': 'Invalid status'}), 400
        
        db = get_db()
        user_role = session.get('user_role', '').lower()
        user_id = session.get('user_id')
        
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return jsonify({'error': 'Machine not found'}), 404
        
        machine_data = machine_doc.to_dict()
        workflow_instance = machine_data.get('workflow_instance')
        
        if not workflow_instance:
            return jsonify({'error': 'No workflow found for this machine'}), 404
        
        # Update the specific stage
        stages = workflow_instance.get('stages', [])
        stage_updated = False
        stage_to_update = None
        
        for stage in stages:
            if stage['name'] == stage_name:
                stage_to_update = stage
                break
        
        if not stage_to_update:
            return jsonify({'error': 'Stage not found'}), 404
        
        # Check if user has permission to update this stage
        if 'admin' not in user_role:
            # Non-admin users can only update stages they are assigned to
            assigned_users = stage_to_update.get('assigned_users', [])
            user_assigned = any(user.get('user_id') == user_id for user in assigned_users)
            
            if not user_assigned:
                return jsonify({'error': 'Access denied - you are not assigned to this stage'}), 403
        
        # Update the stage
        old_status = stage_to_update['status']
        stage_to_update['status'] = new_status
        stage_to_update['notes'] = notes
        
        # Update timestamps
        if new_status == 'in_progress' and old_status == 'pending':
            stage_to_update['started_at'] = datetime.now()
        elif new_status == 'completed' and old_status in ['pending', 'in_progress']:
            stage_to_update['completed_at'] = datetime.now()
            if not stage_to_update.get('started_at'):
                stage_to_update['started_at'] = datetime.now()
        
        # Add user info to the update
        stage_to_update['last_updated_by'] = {
            'user_id': user_id,
            'username': session.get('user_name', 'Unknown'),
            'updated_at': datetime.now()
        }
        
        # Update workflow instance
        workflow_instance['updated_at'] = datetime.now()
        
        # Determine current stage and overall status
        current_stage = 'Terminé'
        workflow_status = 'completed'
        
        for stage in stages:
            if stage['status'] == 'in_progress':
                current_stage = stage['label']
                workflow_status = 'active'
                break
            elif stage['status'] == 'pending':
                current_stage = stage['label']
                workflow_status = 'active'
                break
            elif stage['status'] == 'blocked':
                current_stage = f"{stage['label']} (Bloqué)"
                workflow_status = 'blocked'
                break
        
        # Update machine document
        machine_ref.update({
            'workflow_instance': workflow_instance,
            'workflow_status': workflow_status,
            'current_stage': current_stage,
            'updated_at': datetime.now()
        })
        
        return jsonify({
            'success': True,
            'message': f'Stage {stage_name} updated successfully',
            'current_stage': current_stage,
            'workflow_status': workflow_status
        })
        
    except Exception as e:
        return jsonify({'error': f'Error updating workflow stage: {str(e)}'}), 500

@workflow_bp.route('/workflows/<machine_id>/assign', methods=['POST'])
@login_required
def assign_user_to_stage(machine_id):
    """Assign a user to a workflow stage"""
    if not is_firebase_available():
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        data = request.get_json()
        stage_name = data.get('stage_name')
        user_id = data.get('user_id')
        
        if not stage_name or not user_id:
            return jsonify({'error': 'Stage name and user ID are required'}), 400
        
        db = get_db()
        
        # Get user info
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_doc.to_dict()
        
        # Get machine workflow
        machine_ref = db.collection('machines').document(machine_id)
        machine_doc = machine_ref.get()
        
        if not machine_doc.exists:
            return jsonify({'error': 'Machine not found'}), 404
        
        machine_data = machine_doc.to_dict()
        workflow_instance = machine_data.get('workflow_instance')
        
        if not workflow_instance:
            return jsonify({'error': 'No workflow found for this machine'}), 404
        
        # Update the specific stage with user assignment
        stages = workflow_instance.get('stages', [])
        stage_updated = False
        
        for stage in stages:
            if stage['name'] == stage_name:
                # Add user to assigned users list
                assigned_users = stage.get('assigned_users', [])
                
                # Check if user is already assigned
                user_already_assigned = any(u['user_id'] == user_id for u in assigned_users)
                
                if not user_already_assigned:
                    assigned_users.append({
                        'user_id': user_id,
                        'username': user_data.get('username', 'Unknown'),
                        'role': user_data.get('role', 'Unknown'),
                        'assigned_at': datetime.now()
                    })
                    
                    stage['assigned_users'] = assigned_users
                    stage_updated = True
                else:
                    return jsonify({'error': 'User already assigned to this stage'}), 400
                
                break
        
        if not stage_updated:
            return jsonify({'error': 'Stage not found'}), 404
        
        # Update workflow instance
        workflow_instance['updated_at'] = datetime.now()
        
        # Update machine document
        machine_ref.update({
            'workflow_instance': workflow_instance,
            'updated_at': datetime.now()
        })
        
        return jsonify({
            'success': True,
            'message': f'User {user_data.get("username", "Unknown")} assigned to stage {stage_name}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error assigning user: {str(e)}'}), 500

@workflow_bp.route('/workflow_stages', methods=['GET'])
@login_required
def get_workflow_stages():
    """Get all available workflow stages"""
    if not is_firebase_available():
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        db = get_db()
        
        # Get all workflow stages
        stages_ref = db.collection('workflow_stages').order_by('order')
        stages = stages_ref.stream()
        
        stage_list = []
        for stage in stages:
            stage_data = stage.to_dict()
            stage_data['id'] = stage.id
            stage_list.append(stage_data)
        
        return jsonify({
            'success': True,
            'stages': stage_list
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching stages: {str(e)}'}), 500

@workflow_bp.route('/workflows/dashboard', methods=['GET'])
@login_required
def workflow_dashboard():
    """Get workflow dashboard data"""
    if not is_firebase_available():
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        db = get_db()
        
        # Get all machines with workflows
        machines_ref = db.collection('machines')
        machines = machines_ref.stream()
        
        dashboard_data = {
            'total_workflows': 0,
            'active_workflows': 0,
            'completed_workflows': 0,
            'blocked_workflows': 0,
            'stage_statistics': {
                'material_collection': {'total': 0, 'completed': 0, 'in_progress': 0},
                'assembly': {'total': 0, 'completed': 0, 'in_progress': 0},
                'testing': {'total': 0, 'completed': 0, 'in_progress': 0},
                'delivery': {'total': 0, 'completed': 0, 'in_progress': 0},
                'installation': {'total': 0, 'completed': 0, 'in_progress': 0}
            },
            'recent_activities': []
        }
        
        for machine in machines:
            machine_data = machine.to_dict()
            workflow_instance = machine_data.get('workflow_instance')
            
            if workflow_instance:
                dashboard_data['total_workflows'] += 1
                
                workflow_status = machine_data.get('workflow_status', 'unknown')
                if workflow_status == 'active':
                    dashboard_data['active_workflows'] += 1
                elif workflow_status == 'completed':
                    dashboard_data['completed_workflows'] += 1
                elif workflow_status == 'blocked':
                    dashboard_data['blocked_workflows'] += 1
                
                # Count stage statistics
                stages = workflow_instance.get('stages', [])
                for stage in stages:
                    stage_name = stage['name']
                    if stage_name in dashboard_data['stage_statistics']:
                        dashboard_data['stage_statistics'][stage_name]['total'] += 1
                        
                        if stage['status'] == 'completed':
                            dashboard_data['stage_statistics'][stage_name]['completed'] += 1
                        elif stage['status'] == 'in_progress':
                            dashboard_data['stage_statistics'][stage_name]['in_progress'] += 1
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error fetching dashboard data: {str(e)}'}), 500
