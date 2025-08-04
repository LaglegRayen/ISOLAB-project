#!/usr/bin/env python3
"""
Test script to verify role-based access control for machines and workflows
"""

import firebase_admin
from firebase_admin import credentials, firestore
from blueprints.firebase_config import initialize_firebase,get_db, is_firebase_available
import json

def test_role_based_access():
    """Test role-based access control functionality"""
    initialize_firebase()
    if not is_firebase_available():
        print("❌ Firebase not available")
        return
    
    db = get_db()
    print("✅ Firebase connection established")
    
    # Test 1: Get all users and their roles
    print("\n=== TEST 1: User Roles ===")
    users_ref = db.collection('users')
    users = users_ref.get()
    
    user_list = []
    for user_doc in users:
        user_data = user_doc.to_dict()
        user_info = {
            'id': user_doc.id,
            'username': user_data.get('username'),
            'role': user_data.get('role', 'user'),
            'email': user_data.get('email')
        }
        user_list.append(user_info)
        print(f"User: {user_info['username']} | Role: {user_info['role']} | ID: {user_info['id']}")
    
    # Test 2: Get all machines and their workflow assignments
    print("\n=== TEST 2: Machine Workflow Assignments ===")
    machines_ref = db.collection('machines')
    machines = machines_ref.get()
    
    machine_assignments = {}
    for machine_doc in machines:
        machine_data = machine_doc.to_dict()
        machine_id = machine_doc.id
        machine_name = machine_data.get('nom_machine', 'Unknown')
        
        workflow_instance = machine_data.get('workflow_instance')
        if workflow_instance:
            stages = workflow_instance.get('stages', [])
            assigned_users = []
            
            for stage in stages:
                stage_users = stage.get('assigned_users', [])
                for user in stage_users:
                    user_id = user.get('user_id')
                    if user_id not in assigned_users:
                        assigned_users.append(user_id)
            
            machine_assignments[machine_id] = {
                'name': machine_name,
                'assigned_users': assigned_users
            }
            
            print(f"Machine: {machine_name} ({machine_id})")
            print(f"  Assigned users: {assigned_users}")
    
    # Test 3: Simulate access control for each user
    print("\n=== TEST 3: Access Control Simulation ===")
    for user in user_list:
        user_id = user['id']
        user_role = user['role'].lower()
        username = user['username']
        
        print(f"\n--- User: {username} (Role: {user_role}) ---")
        
        if 'admin' in user_role:
            accessible_machines = list(machine_assignments.keys())
            print(f"✅ Admin access: Can see all {len(accessible_machines)} machines")
        else:
            # Regular user - only machines they're assigned to
            accessible_machines = []
            for machine_id, machine_info in machine_assignments.items():
                if user_id in machine_info['assigned_users']:
                    accessible_machines.append(machine_id)
            
            print(f"🔒 Regular user access: Can see {len(accessible_machines)} machines")
            for machine_id in accessible_machines:
                machine_name = machine_assignments[machine_id]['name']
                print(f"  - {machine_name} ({machine_id})")
    
    # Test 4: Check specific workflow stage permissions
    print("\n=== TEST 4: Workflow Stage Permissions ===")
    for user in user_list:
        user_id = user['id']
        user_role = user['role'].lower()
        username = user['username']
        
        print(f"\n--- Stage permissions for: {username} ---")
        
        for machine_id, machine_info in machine_assignments.items():
            if 'admin' in user_role or user_id in machine_info['assigned_users']:
                # Get detailed stage assignments
                machine_ref = db.collection('machines').document(machine_id)
                machine_doc = machine_ref.get()
                machine_data = machine_doc.to_dict()
                
                workflow_instance = machine_data.get('workflow_instance')
                if workflow_instance:
                    stages = workflow_instance.get('stages', [])
                    
                    user_stages = []
                    for stage in stages:
                        if 'admin' in user_role:
                            user_stages.append(f"{stage['label']} (Admin)")
                        else:
                            assigned_users = stage.get('assigned_users', [])
                            if any(u.get('user_id') == user_id for u in assigned_users):
                                user_stages.append(stage['label'])
                    
                    if user_stages:
                        print(f"  Machine: {machine_info['name']}")
                        print(f"    Can modify stages: {', '.join(user_stages)}")

def main():
    print("🔍 Testing Role-Based Access Control")
    print("=" * 50)
    
    try:
        test_role_based_access()
        print("\n✅ Role-based access control test completed")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    main()
