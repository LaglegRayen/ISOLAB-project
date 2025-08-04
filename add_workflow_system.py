"""
Add workflow system to existing Firestore database
This script will:
1. Create workflow_stages collection with dependencies
2. Add workflow_instance to each machine document
3. Assign users to workflow stages based on roles
"""

import sys
import os
from datetime import datetime
import random

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blueprints.firebase_config import initialize_firebase, get_db, is_firebase_available

def create_workflow_stages():
    """Create workflow stages with dependencies"""
    initialize_firebase()
    
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    db = get_db()
    
    # Define workflow stages with dependencies
    workflow_stages = [
        {
            'name': 'material_collection',
            'label': 'Collecte des matériaux',
            'description': 'Collecte et préparation des matériaux nécessaires',
            'depends_on': [],  # First stage, no dependencies
            'estimated_duration_hours': 4,
            'required_roles': ['technicien', 'gestionnaire'],
            'order': 1,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'assembly',
            'label': 'Assemblage',
            'description': 'Assemblage de la machine',
            'depends_on': ['material_collection'],
            'estimated_duration_hours': 8,
            'required_roles': ['technicien', 'ingenieur'],
            'order': 2,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'testing',
            'label': 'Tests et validation',
            'description': 'Tests de fonctionnement et validation qualité',
            'depends_on': ['assembly'],
            'estimated_duration_hours': 6,
            'required_roles': ['ingenieur', 'technicien'],
            'order': 3,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'delivery',
            'label': 'Livraison',
            'description': 'Transport et livraison chez le client',
            'depends_on': ['testing'],
            'estimated_duration_hours': 4,
            'required_roles': ['chauffeur', 'gestionnaire'],
            'order': 4,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'installation',
            'label': 'Installation',
            'description': 'Installation et mise en service chez le client',
            'depends_on': ['delivery'],
            'estimated_duration_hours': 6,
            'required_roles': ['technicien', 'ingenieur'],
            'order': 5,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]
    
    try:
        print("🔄 Creating workflow stages...")
        
        # Clear existing workflow stages first
        existing_stages = db.collection('workflow_stages').stream()
        for stage in existing_stages:
            stage.reference.delete()
        
        # Add new workflow stages
        stage_ids = {}
        for stage_data in workflow_stages:
            doc_ref = db.collection('workflow_stages').add(stage_data)
            stage_id = doc_ref[1].id
            stage_ids[stage_data['name']] = stage_id
            
            print(f"✅ Created stage: {stage_data['label']} (depends on: {stage_data['depends_on']})")
        
        print(f"✅ Created {len(workflow_stages)} workflow stages")
        return stage_ids
        
    except Exception as e:
        print(f"❌ Error creating workflow stages: {str(e)}")
        return None

def get_existing_users():
    """Get all users from the database"""
    db = get_db()
    
    try:
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        user_data = []
        for user in users:
            user_dict = user.to_dict()
            user_dict['id'] = user.id
            user_data.append(user_dict)
        
        print(f"📋 Found {len(user_data)} users in database")
        return user_data
        
    except Exception as e:
        print(f"❌ Error fetching users: {str(e)}")
        return []

def get_existing_machines():
    """Get all machines from the database"""
    db = get_db()
    
    try:
        machines_ref = db.collection('machines')
        machines = machines_ref.stream()
        
        machine_data = []
        for machine in machines:
            machine_dict = machine.to_dict()
            machine_dict['id'] = machine.id
            machine_data.append(machine_dict)
        
        print(f"🏭 Found {len(machine_data)} machines in database")
        return machine_data
        
    except Exception as e:
        print(f"❌ Error fetching machines: {str(e)}")
        return []

def assign_users_to_stage(stage_name, required_roles, users):
    """Assign users to a workflow stage based on their roles"""
    assigned_users = []
    
    # Filter users by required roles
    eligible_users = []
    for user in users:
        user_role = user.get('role', '').lower()
        if any(role.lower() in user_role for role in required_roles):
            eligible_users.append(user)
    
    # If no users found with exact role match, try broader matching
    if not eligible_users:
        for user in users:
            user_role = user.get('role', '').lower()
            # Broader matching for common roles
            if ('admin' in user_role or 'manager' in user_role or 
                'tech' in user_role or 'ing' in user_role):
                eligible_users.append(user)
    
    # Assign 1-2 users randomly from eligible users
    if eligible_users:
        num_to_assign = min(2, len(eligible_users))
        selected_users = random.sample(eligible_users, num_to_assign)
        
        for user in selected_users:
            assigned_users.append({
                'user_id': user['id'],
                'username': user.get('username', 'Unknown'),
                'role': user.get('role', 'Unknown'),
                'assigned_at': datetime.now()
            })
    
    return assigned_users

def create_workflow_instance(machine, stage_ids, users):
    """Create a workflow instance for a machine"""
    
    # Define workflow stages in order
    stages_order = [
        'material_collection',
        'assembly', 
        'testing',
        'delivery',
        'installation'
    ]
    
    workflow_instance = {
        'machine_id': machine['id'],
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'status': 'active',  # active, completed, cancelled
        'stages': []
    }
    
    # Determine current stage based on machine status
    machine_status = machine.get('status', '').lower()
    current_stage_index = 0
    
    if 'terminé' in machine_status or 'complete' in machine_status:
        current_stage_index = len(stages_order)  # All stages completed
    elif 'cours' in machine_status or 'progress' in machine_status:
        current_stage_index = 2  # Currently in testing stage
    elif 'problème' in machine_status or 'problem' in machine_status:
        current_stage_index = 1  # Problem during assembly
    
    # Create workflow stages
    for i, stage_name in enumerate(stages_order):
        # Determine stage status based on current progress
        if i < current_stage_index:
            stage_status = 'completed'
            completed_at = datetime.now()
            started_at = datetime.now()
        elif i == current_stage_index:
            stage_status = 'in_progress'
            started_at = datetime.now()
            completed_at = None
        else:
            stage_status = 'pending'
            started_at = None
            completed_at = None
        
        # Get dependencies
        depends_on = []
        if i > 0:
            depends_on = [stages_order[i-1]]
        
        # Assign users to this stage
        stage_requirements = {
            'material_collection': ['technicien', 'gestionnaire'],
            'assembly': ['technicien', 'ingenieur'],
            'testing': ['ingenieur', 'technicien'],
            'delivery': ['chauffeur', 'gestionnaire'],
            'installation': ['technicien', 'ingenieur']
        }
        
        required_roles = stage_requirements.get(stage_name, ['technicien'])
        assigned_users = assign_users_to_stage(stage_name, required_roles, users)
        
        stage_data = {
            'name': stage_name,
            'label': {
                'material_collection': 'Collecte des matériaux',
                'assembly': 'Assemblage',
                'testing': 'Tests et validation',
                'delivery': 'Livraison',
                'installation': 'Installation'
            }[stage_name],
            'status': stage_status,
            'depends_on': depends_on,
            'assigned_users': assigned_users,
            'started_at': started_at,
            'completed_at': completed_at,
            'estimated_duration_hours': {
                'material_collection': 4,
                'assembly': 8,
                'testing': 6,
                'delivery': 4,
                'installation': 6
            }[stage_name],
            'order': i + 1,
            'notes': '',
            'attachments': []
        }
        
        workflow_instance['stages'].append(stage_data)
    
    return workflow_instance

def add_workflow_to_machines():
    """Add workflow instances to all existing machines"""
    initialize_firebase()
    
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    db = get_db()
    
    try:
        # Get existing data
        print("🔄 Fetching existing data...")
        stage_ids = create_workflow_stages()
        if not stage_ids:
            return False
        
        users = get_existing_users()
        machines = get_existing_machines()
        
        if not users:
            print("⚠️  No users found, creating default users...")
            users = create_default_users(db)
        
        if not machines:
            print("⚠️  No machines found in database!")
            return False
        
        print(f"\n🔄 Adding workflow instances to {len(machines)} machines...")
        
        updated_count = 0
        for machine in machines:
            try:
                # Create workflow instance for this machine
                workflow_instance = create_workflow_instance(machine, stage_ids, users)
                
                # Update machine document with workflow instance
                machine_ref = db.collection('machines').document(machine['id'])
                machine_ref.update({
                    'workflow_instance': workflow_instance,
                    'workflow_status': workflow_instance['status'],
                    'current_stage': get_current_stage_name(workflow_instance),
                    'updated_at': datetime.now()
                })
                
                current_stage = get_current_stage_name(workflow_instance)
                print(f"✅ Updated machine {machine.get('serialNumber', 'Unknown')} - Current stage: {current_stage}")
                updated_count += 1
                
            except Exception as e:
                print(f"❌ Error updating machine {machine.get('serialNumber', 'Unknown')}: {str(e)}")
        
        print(f"\n🎉 Successfully updated {updated_count} machines with workflow instances!")
        print("\n📊 Workflow Summary:")
        print("Stages created:")
        for stage_name in ['material_collection', 'assembly', 'testing', 'delivery', 'installation']:
            print(f"  • {stage_name}")
        
        print(f"\nMachines updated: {updated_count}")
        print("Each machine now has a complete workflow tracking system!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding workflows to machines: {str(e)}")
        return False

def get_current_stage_name(workflow_instance):
    """Get the name of the current stage in the workflow"""
    for stage in workflow_instance['stages']:
        if stage['status'] == 'in_progress':
            return stage['label']
    
    # If no in_progress stage, check for pending stages
    for stage in workflow_instance['stages']:
        if stage['status'] == 'pending':
            return stage['label']
    
    return 'Terminé'

def create_default_users(db):
    """Create default users if none exist"""
    default_users = [
        {
            'username': 'admin',
            'email': 'admin@isolab.tn',
            'role': 'Administrateur',
            'full_name': 'Administrateur Principal',
            'phone': '70123456',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'status': 'active'
        },
        {
            'username': 'technicien1',
            'email': 'tech1@isolab.tn',
            'role': 'Technicien',
            'full_name': 'Ahmed Technicien',
            'phone': '70123457',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'status': 'active'
        },
        {
            'username': 'ingenieur1',
            'email': 'ing1@isolab.tn',
            'role': 'Ingénieur',
            'full_name': 'Mohamed Ingénieur',
            'phone': '70123458',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'status': 'active'
        },
        {
            'username': 'gestionnaire1',
            'email': 'gest1@isolab.tn',
            'role': 'Gestionnaire',
            'full_name': 'Fatma Gestionnaire',
            'phone': '70123459',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'status': 'active'
        }
    ]
    
    created_users = []
    for user_data in default_users:
        doc_ref = db.collection('users').add(user_data)
        user_data['id'] = doc_ref[1].id
        created_users.append(user_data)
        print(f"✅ Created user: {user_data['full_name']} ({user_data['role']})")
    
    return created_users

def view_workflow_status():
    """View current workflow status of all machines"""
    initialize_firebase()
    
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    db = get_db()
    
    try:
        machines_ref = db.collection('machines')
        machines = machines_ref.stream()
        
        print("\n📊 Current Workflow Status:")
        print("=" * 80)
        
        for machine in machines:
            machine_data = machine.to_dict()
            serial = machine_data.get('serialNumber', 'Unknown')
            workflow = machine_data.get('workflow_instance', {})
            
            if workflow:
                current_stage = machine_data.get('current_stage', 'Unknown')
                status = workflow.get('status', 'Unknown')
                
                print(f"\n🏭 Machine: {serial}")
                print(f"   Status: {status}")
                print(f"   Current Stage: {current_stage}")
                
                stages = workflow.get('stages', [])
                for stage in stages:
                    status_icon = {
                        'completed': '✅',
                        'in_progress': '🔄',
                        'pending': '⏳'
                    }.get(stage['status'], '❓')
                    
                    assigned_users = stage.get('assigned_users', [])
                    user_names = [user.get('username', 'Unknown') for user in assigned_users]
                    
                    print(f"     {status_icon} {stage['label']} - {stage['status']} - Users: {', '.join(user_names) if user_names else 'None'}")
            else:
                print(f"\n🏭 Machine: {serial} - No workflow assigned")
        
        return True
        
    except Exception as e:
        print(f"❌ Error viewing workflow status: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Workflow System Setup")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "view":
            view_workflow_status()
        elif sys.argv[1] == "stages":
            create_workflow_stages()
        else:
            print("Available commands:")
            print("  python add_workflow_system.py        - Add workflow to all machines")
            print("  python add_workflow_system.py view   - View current workflow status")
            print("  python add_workflow_system.py stages - Create workflow stages only")
    else:
        success = add_workflow_to_machines()
        
        if success:
            print("\n📝 Next steps:")
            print("1. Run 'python add_workflow_system.py view' to see workflow status")
            print("2. Implement workflow tracking in your web interface")
            print("3. Add workflow management endpoints to your Flask app")
