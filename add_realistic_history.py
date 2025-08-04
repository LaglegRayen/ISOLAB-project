#!/usr/bin/env python3
"""
Add realistic machine history with actual user IDs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blueprints.firebase_config import initialize_firebase, get_db, is_firebase_available
from datetime import datetime, timedelta
import random

def get_user_ids():
    """Get actual user IDs from the database"""
    print("📋 Getting user IDs...")
    
    db = get_db()
    users_ref = db.collection('users')
    users_docs = users_ref.stream()
    
    user_mapping = {}
    for doc in users_docs:
        user_data = doc.to_dict()
        username = user_data.get('username')
        if username:
            user_mapping[username] = doc.id
            print(f"   ✅ Found user: {username} - ID: {doc.id}")
    
    return user_mapping

def get_machines():
    """Get all machines from the database"""
    print("🔧 Getting machines...")
    
    db = get_db()
    machines_ref = db.collection('machines')
    machines_docs = machines_ref.stream()
    
    machines = []
    for doc in machines_docs:
        machine_data = doc.to_dict()
        machine_data['id'] = doc.id
        machines.append(machine_data)
        print(f"   ✅ Found machine: {machine_data.get('serialNumber')} - Current stage: {machine_data.get('current_stage')}")
    
    return machines

def create_realistic_history(user_mapping, machines):
    """Create realistic machine history with actual user IDs"""
    print("📝 Creating realistic machine history...")
    
    db = get_db()
    history_ref = db.collection('machine_history')
    
    # Clear existing history
    existing_history = history_ref.stream()
    for doc in existing_history:
        doc.reference.delete()
    print("   🗑️ Cleared existing history")
    
    # Stage progression mapping
    stage_progression = [
        'material_collection',
        'assembly', 
        'testing',
        'delivery',
        'installation'
    ]
    
    stage_labels = {
        'material_collection': 'Collecte des matériaux',
        'assembly': 'Assemblage',
        'testing': 'Tests et validation',
        'delivery': 'Livraison',
        'installation': 'Installation'
    }
    
    stage_users = {
        'material_collection': user_mapping.get('supervisor'),
        'assembly': user_mapping.get('assembly_tech'),
        'testing': user_mapping.get('testing_tech'),
        'delivery': user_mapping.get('delivery_tech'),
        'installation': user_mapping.get('installation_tech')
    }
    
    stage_usernames = {
        'material_collection': 'supervisor',
        'assembly': 'assembly_tech',
        'testing': 'testing_tech',
        'delivery': 'delivery_tech',
        'installation': 'installation_tech'
    }
    
    history_count = 0
    
    for machine in machines:
        machine_id = machine['id']
        current_stage = machine.get('current_stage')
        serial_number = machine.get('serialNumber')
        
        if not current_stage:
            continue
        
        # Find the index of current stage
        try:
            current_stage_index = stage_progression.index(current_stage)
        except ValueError:
            continue
        
        # Create history for all completed stages (before current stage)
        for i in range(current_stage_index):
            stage_name = stage_progression[i]
            
            # Calculate realistic dates
            days_ago_start = random.randint(15 + (current_stage_index - i) * 3, 30 + (current_stage_index - i) * 5)
            days_ago_end = random.randint(10 + (current_stage_index - i) * 2, days_ago_start - 1)
            
            history_entry = {
                'machine_id': machine_id,
                'machine_serial': serial_number,
                'stage_name': stage_name,
                'stage_label': stage_labels[stage_name],
                'status': 'completed',
                'assigned_user_id': stage_users.get(stage_name),
                'assigned_username': stage_usernames.get(stage_name),
                'started_at': datetime.now() - timedelta(days=days_ago_start),
                'completed_at': datetime.now() - timedelta(days=days_ago_end),
                'duration_hours': random.uniform(3.0, 12.0),
                'remarks': f'{stage_labels[stage_name]} terminé avec succès',
                'created_at': datetime.now() - timedelta(days=days_ago_end)
            }
            
            history_ref.add(history_entry)
            history_count += 1
            print(f"   ✅ Added history: {serial_number} - {stage_labels[stage_name]} (completed)")
    
    # Add some additional random activities for variety
    additional_activities = [
        {
            'stage_name': 'quality_check',
            'stage_label': 'Contrôle qualité',
            'status': 'completed',
            'assigned_user_id': user_mapping.get('testing_tech'),
            'assigned_username': 'testing_tech'
        },
        {
            'stage_name': 'documentation',
            'stage_label': 'Documentation technique',
            'status': 'completed',
            'assigned_user_id': user_mapping.get('admin'),
            'assigned_username': 'admin'
        },
        {
            'stage_name': 'client_training',
            'stage_label': 'Formation client',
            'status': 'completed',
            'assigned_user_id': user_mapping.get('installation_tech'),
            'assigned_username': 'installation_tech'
        }
    ]
    
    for i, activity in enumerate(additional_activities):
        # Use a random machine for these activities
        random_machine = random.choice(machines)
        
        history_entry = {
            'machine_id': random_machine['id'],
            'machine_serial': random_machine.get('serialNumber'),
            'stage_name': activity['stage_name'],
            'stage_label': activity['stage_label'],
            'status': activity['status'],
            'assigned_user_id': activity['assigned_user_id'],
            'assigned_username': activity['assigned_username'],
            'started_at': datetime.now() - timedelta(days=random.randint(1, 7)),
            'completed_at': datetime.now() - timedelta(hours=random.randint(2, 48)),
            'duration_hours': random.uniform(1.0, 4.0),
            'remarks': f'{activity["stage_label"]} effectué',
            'created_at': datetime.now() - timedelta(hours=random.randint(2, 48))
        }
        
        history_ref.add(history_entry)
        history_count += 1
        print(f"   ✅ Added activity: {random_machine.get('serialNumber')} - {activity['stage_label']}")
    
    return history_count

def main():
    """Main function to add realistic history"""
    print("🚀 Adding realistic machine history...")
    
    # Initialize Firebase
    if not initialize_firebase():
        print("❌ Failed to initialize Firebase!")
        return False
    
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    try:
        # Get user IDs
        user_mapping = get_user_ids()
        
        # Get machines
        machines = get_machines()
        
        # Create realistic history
        history_count = create_realistic_history(user_mapping, machines)
        
        print("\n" + "="*50)
        print("✅ REALISTIC HISTORY ADDED!")
        print("="*50)
        print(f"📊 Summary:")
        print(f"   • {len(user_mapping)} users found")
        print(f"   • {len(machines)} machines processed")
        print(f"   • {history_count} history entries created")
        print("\n🎉 Recent activities should now display real data!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding history: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ History data ready! Refresh the dashboard to see recent activities.")
    else:
        print("\n💥 Failed to add history data.")
