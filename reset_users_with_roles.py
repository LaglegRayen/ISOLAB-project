#!/usr/bin/env python3
"""
Script to reset users with proper roles and workflow assignments
This will remove old users and create new ones compatible with the role-based access control system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blueprints.firebase_config import initialize_firebase, get_db, is_firebase_available
from datetime import datetime
import hashlib

def hash_password(password):
    """Simple password hashing (use proper hashing in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def clear_old_users():
    """Remove all existing users"""
    print("🗑️ Clearing old users...")
    
    db = get_db()
    users_ref = db.collection('users')
    users = users_ref.get()
    
    deleted_count = 0
    for user_doc in users:
        user_doc.reference.delete()
        deleted_count += 1
    
    print(f"✅ Deleted {deleted_count} old users")

def create_new_users():
    """Create new users with proper role structure"""
    print("👥 Creating new users with proper roles...")
    
    db = get_db()
    users_ref = db.collection('users')
    
    # Define new users with proper structure
    new_users = [
        {
            'username': 'admin',
            'email': 'admin@isolab.com',
            'password': hash_password('admin123'),
            'role': 'admin',
            'first_name': 'Administrator',
            'last_name': 'System',
            'department': 'IT',
            'phone': '+216 20 123 456',
            'created_at': datetime.now(),
            'is_active': True,
            'permissions': {
                'can_manage_users': True,
                'can_manage_clients': True,
                'can_manage_machines': True,
                'can_manage_workflows': True,
                'can_view_all_machines': True,
                'can_modify_all_stages': True
            }
        },
        {
            'username': 'technicien1',
            'email': 'tech1@isolab.com', 
            'password': hash_password('tech123'),
            'role': 'user',
            'first_name': 'Ahmed',
            'last_name': 'Ben Ali',
            'department': 'Technique',
            'specialization': 'Assembly',
            'phone': '+216 25 789 123',
            'created_at': datetime.now(),
            'is_active': True,
            'permissions': {
                'can_manage_users': False,
                'can_manage_clients': False,
                'can_manage_machines': False,
                'can_manage_workflows': False,
                'can_view_all_machines': False,
                'can_modify_all_stages': False
            }
        },
        {
            'username': 'technicien2',
            'email': 'tech2@isolab.com',
            'password': hash_password('tech123'),
            'role': 'user', 
            'first_name': 'Fatma',
            'last_name': 'Hadji',
            'department': 'Technique',
            'specialization': 'Testing',
            'phone': '+216 26 456 789',
            'created_at': datetime.now(),
            'is_active': True,
            'permissions': {
                'can_manage_users': False,
                'can_manage_clients': False,
                'can_manage_machines': False,
                'can_manage_workflows': False,
                'can_view_all_machines': False,
                'can_modify_all_stages': False
            }
        },
        {
            'username': 'technicien3',
            'email': 'tech3@isolab.com',
            'password': hash_password('tech123'),
            'role': 'user',
            'first_name': 'Mohamed',
            'last_name': 'Trabelsi',
            'department': 'Logistique',
            'specialization': 'Delivery & Installation',
            'phone': '+216 27 321 654',
            'created_at': datetime.now(),
            'is_active': True,
            'permissions': {
                'can_manage_users': False,
                'can_manage_clients': False,
                'can_manage_machines': False,
                'can_manage_workflows': False,
                'can_view_all_machines': False,
                'can_modify_all_stages': False
            }
        },
        {
            'username': 'supervisor',
            'email': 'supervisor@isolab.com',
            'password': hash_password('super123'),
            'role': 'supervisor',
            'first_name': 'Leila',
            'last_name': 'Gharbi',
            'department': 'Production',
            'phone': '+216 28 987 654',
            'created_at': datetime.now(),
            'is_active': True,
            'permissions': {
                'can_manage_users': False,
                'can_manage_clients': True,
                'can_manage_machines': True,
                'can_manage_workflows': True,
                'can_view_all_machines': True,
                'can_modify_all_stages': False  # Can view but not modify all stages
            }
        }
    ]
    
    user_ids = {}
    for user_data in new_users:
        # Add user to Firestore
        doc_ref = users_ref.add(user_data)
        user_id = doc_ref[1].id
        user_ids[user_data['username']] = user_id
        
        print(f"✅ Created user: {user_data['username']} ({user_data['role']}) - ID: {user_id}")
    
    return user_ids

def update_workflow_assignments(user_ids):
    """Update workflow assignments with the new user IDs"""
    print("🔄 Updating workflow assignments...")
    
    db = get_db()
    machines_ref = db.collection('machines')
    machines = machines_ref.get()
    
    updated_count = 0
    for machine_doc in machines:
        machine_data = machine_doc.to_dict()
        workflow_instance = machine_data.get('workflow_instance')
        
        if workflow_instance and 'stages' in workflow_instance:
            stages = workflow_instance['stages']
            
            # Update stage assignments based on specializations
            for stage in stages:
                stage_name = stage['name']
                
                # Clear old assignments
                stage['assigned_users'] = []
                
                # Assign users based on stage type and specialization
                if stage_name == 'material_collection':
                    # Assign supervisor to material collection
                    if 'supervisor' in user_ids:
                        stage['assigned_users'].append({
                            'user_id': user_ids['supervisor'],
                            'username': 'supervisor',
                            'role': 'supervisor',
                            'assigned_at': datetime.now()
                        })
                
                elif stage_name == 'assembly':
                    # Assign assembly specialist
                    if 'technicien1' in user_ids:
                        stage['assigned_users'].append({
                            'user_id': user_ids['technicien1'],
                            'username': 'technicien1',
                            'role': 'user',
                            'assigned_at': datetime.now()
                        })
                
                elif stage_name == 'testing':
                    # Assign testing specialist
                    if 'technicien2' in user_ids:
                        stage['assigned_users'].append({
                            'user_id': user_ids['technicien2'],
                            'username': 'technicien2', 
                            'role': 'user',
                            'assigned_at': datetime.now()
                        })
                
                elif stage_name in ['delivery', 'installation']:
                    # Assign delivery/installation specialist
                    if 'technicien3' in user_ids:
                        stage['assigned_users'].append({
                            'user_id': user_ids['technicien3'],
                            'username': 'technicien3',
                            'role': 'user', 
                            'assigned_at': datetime.now()
                        })
            
            # Update the machine document
            workflow_instance['updated_at'] = datetime.now()
            machine_doc.reference.update({
                'workflow_instance': workflow_instance,
                'updated_at': datetime.now()
            })
            
            updated_count += 1
    
    print(f"✅ Updated workflow assignments for {updated_count} machines")

def print_login_credentials():
    """Print login credentials for testing"""
    print("\n" + "="*60)
    print("🔑 LOGIN CREDENTIALS FOR TESTING")
    print("="*60)
    
    credentials = [
        ("admin", "admin123", "Full admin access - can see and modify everything"),
        ("technicien1", "tech123", "Assembly specialist - can see assigned machines only"),
        ("technicien2", "tech123", "Testing specialist - can see assigned machines only"),
        ("technicien3", "tech123", "Delivery/Installation - can see assigned machines only"),
        ("supervisor", "super123", "Supervisor - can see all machines, limited modifications")
    ]
    
    for username, password, description in credentials:
        print(f"\nUsername: {username}")
        print(f"Password: {password}")
        print(f"Role: {description}")
    
    print("\n" + "="*60)
    print("💡 TEST SCENARIOS:")
    print("1. Login as 'admin' - should see all machines and modify any stage")
    print("2. Login as 'technicien1' - should only see machines with assembly stages assigned")
    print("3. Login as 'technicien2' - should only see machines with testing stages assigned") 
    print("4. Login as 'technicien3' - should only see machines with delivery/installation assigned")
    print("5. Login as 'supervisor' - should see all machines but limited stage modifications")
    print("="*60)

def main():
    print("🔄 ISOLAB User Reset & Role-Based Access Setup")
    print("="*60)
    
    try:
        # Initialize Firebase
        initialize_firebase()
        if not is_firebase_available():
            print("❌ Firebase not available")
            return
        
        print("✅ Firebase connection established")
        
        # Step 1: Clear old users
        clear_old_users()
        
        # Step 2: Create new users with proper roles
        user_ids = create_new_users()
        
        # Step 3: Update workflow assignments
        update_workflow_assignments(user_ids)
        
        # Step 4: Print login credentials
        print_login_credentials()
        
        print(f"\n✅ User reset completed successfully!")
        print("🚀 You can now test the role-based access control system!")
        
    except Exception as e:
        print(f"\n❌ Error during user reset: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
