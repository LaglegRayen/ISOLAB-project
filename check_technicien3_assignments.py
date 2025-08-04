#!/usr/bin/env python3
"""
Test script to check technicien3's workflow assignments
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blueprints.firebase_config import initialize_firebase, get_db, is_firebase_available
from google.cloud.firestore_v1.base_query import FieldFilter

def check_technicien3_assignments():
    """Check if technicien3 has workflow assignments"""
    
    print("🔍 Checking technicien3's workflow assignments...")
    print("=" * 60)
    
    try:
        # Initialize Firebase
        initialize_firebase()
        if not is_firebase_available():
            print("❌ Firebase not available")
            return
        
        db = get_db()
        
        # Find technicien3 user by email
        print("1. Looking for user with email: tech3@isolab.com")
        users = db.collection('users').where(filter=FieldFilter('email', '==', 'tech3@isolab.com')).get()
        
        if not users:
            print("❌ User not found with email tech3@isolab.com")
            
            # Try by username
            print("   Trying by username: technicien3")
            users = db.collection('users').where(filter=FieldFilter('username', '==', 'technicien3')).get()
            
            if not users:
                print("❌ User not found with username technicien3 either")
                
                # List all users to see what we have
                print("\n📋 All users in database:")
                all_users = db.collection('users').get()
                for user_doc in all_users:
                    user_data = user_doc.to_dict()
                    print(f"   - {user_data.get('username')} | {user_data.get('email')} | {user_data.get('role')}")
                return
        
        user_doc = users[0]
        user_data = user_doc.to_dict()
        user_id = user_doc.id
        
        print(f"✅ User found:")
        print(f"   ID: {user_id}")
        print(f"   Username: {user_data.get('username')}")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Role: {user_data.get('role')}")
        print(f"   Department: {user_data.get('department')}")
        print(f"   Specialization: {user_data.get('specialization')}")
        
        # Check workflow assignments
        print(f"\n2. Checking workflow assignments for user ID: {user_id}")
        machines = db.collection('machines').get()
        
        assigned_machines = []
        total_machines = 0
        
        for machine_doc in machines:
            total_machines += 1
            machine_data = machine_doc.to_dict()
            machine_id = machine_doc.id
            machine_name = machine_data.get('nom_machine', 'Unknown')
            
            workflow_instance = machine_data.get('workflow_instance')
            if workflow_instance:
                stages = workflow_instance.get('stages', [])
                
                machine_stages = []
                for stage in stages:
                    assigned_users = stage.get('assigned_users', [])
                    for assigned_user in assigned_users:
                        if assigned_user.get('user_id') == user_id:
                            machine_stages.append(stage.get('label', stage.get('name')))
                            break
                
                if machine_stages:
                    assigned_machines.append({
                        'machine_id': machine_id,
                        'machine_name': machine_name,
                        'stages': machine_stages
                    })
        
        print(f"📊 Results:")
        print(f"   Total machines in database: {total_machines}")
        print(f"   Machines assigned to technicien3: {len(assigned_machines)}")
        
        if assigned_machines:
            print(f"\n✅ Assignments found:")
            for i, assignment in enumerate(assigned_machines, 1):
                print(f"   {i}. {assignment['machine_name']} ({assignment['machine_id']})")
                print(f"      Stages: {', '.join(assignment['stages'])}")
        else:
            print(f"\n❌ No assignments found for technicien3!")
            
            # Let's check what stages technicien3 should be assigned to
            print(f"\n🔍 Checking what stages technicien3 should have...")
            print(f"   Specialization: {user_data.get('specialization')}")
            
            # Check a sample machine to see stage structure
            if total_machines > 0:
                sample_machine = db.collection('machines').limit(1).get()[0]
                sample_data = sample_machine.to_dict()
                workflow_instance = sample_data.get('workflow_instance')
                
                if workflow_instance:
                    stages = workflow_instance.get('stages', [])
                    print(f"\n📋 Available stages in workflow:")
                    for stage in stages:
                        stage_name = stage.get('name')
                        stage_label = stage.get('label')
                        assigned_users = stage.get('assigned_users', [])
                        print(f"   - {stage_label} ({stage_name})")
                        print(f"     Assigned users: {len(assigned_users)}")
                        for user in assigned_users:
                            print(f"       * {user.get('username')} ({user.get('user_id')})")
        
        print(f"\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error during check: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    check_technicien3_assignments()

if __name__ == "__main__":
    main()
