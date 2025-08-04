#!/usr/bin/env python3
"""
Complete Workflow System Restructure
- Separate stages collection with dependencies
- Machines with only current_stage (no complex workflow_instance)
- Machine history for tracking completed tasks
- One user per stage type, one machine per current stage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blueprints.firebase_config import initialize_firebase, get_db, is_firebase_available
from datetime import datetime, timedelta
import hashlib
import random

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def clear_all_data():
    """Clear all existing data"""
    print("🗑️ Clearing all existing data...")
    
    db = get_db()
    collections_to_clear = ['machines', 'clients', 'users', 'workflow_stages', 'machine_history', 'stages']
    
    total_deleted = 0
    for collection_name in collections_to_clear:
        try:
            collection_ref = db.collection(collection_name)
            docs = collection_ref.stream()
            count = 0
            for doc in docs:
                doc.reference.delete()
                count += 1
            print(f"   ✅ Cleared {count} documents from {collection_name}")
            total_deleted += count
        except Exception as e:
            print(f"   ⚠️ Error clearing {collection_name}: {str(e)}")
    
    print(f"✅ Total cleared: {total_deleted} documents")

def create_stage_definitions():
    """Create separate stages collection with dependencies"""
    print("🔧 Creating stage definitions...")
    
    db = get_db()
    stages_ref = db.collection('stages')
    
    stage_definitions = [
        {
            'name': 'material_collection',
            'label': 'Collecte des matériaux',
            'order': 1,
            'estimated_duration_hours': 4,
            'depends_on': [],  # No dependencies
            'required_role': 'supervisor',
            'description': 'Collection et préparation des matériaux nécessaires',
            'created_at': datetime.now(),
            'is_active': True
        },
        {
            'name': 'assembly',
            'label': 'Assemblage',
            'order': 2,
            'estimated_duration_hours': 8,
            'depends_on': ['material_collection'],
            'required_role': 'assembly_tech',
            'description': 'Assemblage des composants de la machine',
            'created_at': datetime.now(),
            'is_active': True
        },
        {
            'name': 'testing',
            'label': 'Tests et validation',
            'order': 3,
            'estimated_duration_hours': 6,
            'depends_on': ['assembly'],
            'required_role': 'testing_tech',
            'description': 'Tests de fonctionnement et validation qualité',
            'created_at': datetime.now(),
            'is_active': True
        },
        {
            'name': 'delivery',
            'label': 'Livraison',
            'order': 4,
            'estimated_duration_hours': 4,
            'depends_on': ['testing'],
            'required_role': 'delivery_tech',
            'description': 'Préparation et livraison chez le client',
            'created_at': datetime.now(),
            'is_active': True
        },
        {
            'name': 'installation',
            'label': 'Installation',
            'order': 5,
            'estimated_duration_hours': 6,
            'depends_on': ['delivery'],
            'required_role': 'installation_tech',
            'description': 'Installation et mise en service chez le client',
            'created_at': datetime.now(),
            'is_active': True
        }
    ]
    
    stage_ids = {}
    for stage_def in stage_definitions:
        doc_ref = stages_ref.add(stage_def)
        stage_id = doc_ref[1].id
        stage_ids[stage_def['name']] = stage_id
        print(f"   ✅ Created stage: {stage_def['label']} - ID: {stage_id}")
    
    return stage_ids

def create_specialized_users():
    """Create users with specific role assignments (one role per user)"""
    print("👥 Creating specialized users...")
    
    db = get_db()
    users_ref = db.collection('users')
    
    specialized_users = [
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
            'stage_access': 'all',  # Admin can access all stages
            'can_validate_all': True
        },
        {
            'username': 'supervisor',
            'email': 'supervisor@isolab.com',
            'password': hash_password(' '),
            'role': 'supervisor',
            'first_name': 'Leila',
            'last_name': 'Gharbi',
            'department': 'Production',
            'phone': '+216 28 987 654',
            'created_at': datetime.now(),
            'is_active': True,
            'stage_access': 'material_collection',  # Only material collection
            'specialization': 'Material Management'
        },
        {
            'username': 'assembly_tech',
            'email': 'assembly@isolab.com',
            'password': hash_password('tech123'),
            'role': 'assembly_tech',
            'first_name': 'Ahmed',
            'last_name': 'Ben Ali',
            'department': 'Production',
            'phone': '+216 25 789 123',
            'created_at': datetime.now(),
            'is_active': True,
            'stage_access': 'assembly',  # Only assembly
            'specialization': 'Machine Assembly'
        },
        {
            'username': 'testing_tech',
            'email': 'testing@isolab.com',
            'password': hash_password('tech123'),
            'role': 'testing_tech',
            'first_name': 'Fatma',
            'last_name': 'Hadji',
            'department': 'Quality',
            'phone': '+216 26 456 789',
            'created_at': datetime.now(),
            'is_active': True,
            'stage_access': 'testing',  # Only testing
            'specialization': 'Quality Testing'
        },
        {
            'username': 'delivery_tech',
            'email': 'delivery@isolab.com',
            'password': hash_password('tech123'),
            'role': 'delivery_tech',
            'first_name': 'Mohamed',
            'last_name': 'Trabelsi',
            'department': 'Logistics',
            'phone': '+216 27 321 654',
            'created_at': datetime.now(),
            'is_active': True,
            'stage_access': 'delivery',  # Only delivery
            'specialization': 'Delivery & Logistics'
        },
        {
            'username': 'installation_tech',
            'email': 'installation@isolab.com',
            'password': hash_password('tech123'),
            'role': 'installation_tech',
            'first_name': 'Youssef',
            'last_name': 'Mansouri',
            'department': 'Field Service',
            'phone': '+216 29 654 321',
            'created_at': datetime.now(),
            'is_active': True,
            'stage_access': 'installation',  # Only installation
            'specialization': 'On-site Installation'
        }
    ]
    
    user_ids = {}
    for user_data in specialized_users:
        doc_ref = users_ref.add(user_data)
        user_id = doc_ref[1].id
        user_ids[user_data['username']] = user_id
        print(f"   ✅ Created user: {user_data['username']} ({user_data['role']}) - Access: {user_data.get('stage_access', 'none')}")
    
    return user_ids

def create_realistic_clients():
    """Create realistic client data"""
    print("🏢 Creating realistic clients...")
    
    db = get_db()
    clients_ref = db.collection('clients')
    
    clients_data = [
        {
            'clientName': 'Mohamed Abdellaoui',
            'clientSociety': 'Ferme Abdellaoui',
            'clientEmail': 'hamma.abdellaoui@gmail.com',
            'clientPhone': '21907382',
            'clientAddress': 'Route de Mahres, Sfax',
            'clientLocation': 'Sfax',
            'dateAdded': datetime.now() - timedelta(days=30),
            'created_by': 'admin',
            'is_active': True
        },
        {
            'clientName': 'Amina Ben Salem',
            'clientSociety': 'Exploitation Ben Salem',
            'clientEmail': 'amina.bensalem@agricultural.tn',
            'clientPhone': '22156789',
            'clientAddress': 'Zone Industrielle, Sousse',
            'clientLocation': 'Sousse',
            'dateAdded': datetime.now() - timedelta(days=25),
            'created_by': 'admin',
            'is_active': True
        },
        {
            'clientName': 'Karim Jemli',
            'clientSociety': 'Coopérative Jemli',
            'clientEmail': 'k.jemli@coop-agri.tn',
            'clientPhone': '23445566',
            'clientAddress': 'Douar Hicher, Manouba',
            'clientLocation': 'Manouba',
            'dateAdded': datetime.now() - timedelta(days=20),
            'created_by': 'admin',
            'is_active': True
        },
        {
            'clientName': 'Salma Agrebi',
            'clientSociety': 'Ferme Moderne Agrebi',
            'clientEmail': 'salma.agrebi@modernfarm.tn',
            'clientPhone': '24778899',
            'clientAddress': 'Route de Kairouan, Kasserine',
            'clientLocation': 'Kasserine',
            'dateAdded': datetime.now() - timedelta(days=15),
            'created_by': 'admin',
            'is_active': True
        },
        {
            'clientName': 'Hedi Bouaziz',
            'clientSociety': 'Société Agricole Bouaziz',
            'clientEmail': 'hedi.bouaziz@agribouaziz.com',
            'clientPhone': '25889900',
            'clientAddress': 'Centre Ville, Bizerte',
            'clientLocation': 'Bizerte',
            'dateAdded': datetime.now() - timedelta(days=10),
            'created_by': 'admin',
            'is_active': True
        }
    ]
    
    client_ids = {}
    for client_data in clients_data:
        doc_ref = clients_ref.add(client_data)
        client_id = doc_ref[1].id
        client_ids[client_data['clientName']] = client_id
        print(f"   ✅ Created client: {client_data['clientName']} - {client_data['clientLocation']}")
    
    return client_ids

def create_simple_machines(client_ids, user_ids):
    """Create machines with simple current_stage structure"""
    print("🔧 Creating machines with simplified structure...")
    
    db = get_db()
    machines_ref = db.collection('machines')
    
    # Get available stages
    stages = ['material_collection', 'assembly', 'testing', 'delivery', 'installation']
    stage_users = {
        'material_collection': user_ids.get('supervisor'),
        'assembly': user_ids.get('assembly_tech'),
        'testing': user_ids.get('testing_tech'),
        'delivery': user_ids.get('delivery_tech'),
        'installation': user_ids.get('installation_tech')
    }
    
    client_names = list(client_ids.keys())
    machines_data = []
    
    # Create 8 machines in different stages
    for i in range(8):
        client_name = client_names[i % len(client_names)]
        current_stage = stages[i % len(stages)]  # Distribute across stages
        
        machine_data = {
            'serialNumber': f'OLIVIA-{str(i+1).zfill(3)}',
            'ficheNumber': f'FT-{str(i+1).zfill(3)}',
            'machineType': random.choice(['Olivia Standard', 'Olivia Premium', 'Olivia Compact']),
            'clientId': client_ids[client_name],
            'clientName': client_name,
            'clientSociety': client_name,  # Simplified
            'status': 'En cours',
            'current_stage': current_stage,
            'current_stage_label': {
                'material_collection': 'Collecte des matériaux',
                'assembly': 'Assemblage',
                'testing': 'Tests et validation',
                'delivery': 'Livraison',
                'installation': 'Installation'
            }[current_stage],
            'assigned_user_id': stage_users.get(current_stage),
            'assigned_username': {
                'material_collection': 'supervisor',
                'assembly': 'assembly_tech',
                'testing': 'testing_tech',
                'delivery': 'delivery_tech',
                'installation': 'installation_tech'
            }[current_stage],
            'stage_started_at': datetime.now() - timedelta(days=random.randint(1, 10)),
            'prixHT': random.randint(80000, 120000),
            'prixTTC': 0,
            'paymentStatus': random.choice(['En cours', 'Payé', 'En attente']),
            'paymentType': random.choice(['Crédit', 'Espèces', 'Virement']),
            'facturation': random.choice(['Facturée', 'Non facturée']),
            'confirmation': random.choice(['Confirmée', 'En attente']),
            'remarques': f'Machine en étape {current_stage}',
            'dateAdded': datetime.now() - timedelta(days=random.randint(5, 30)),
            'dateUpdated': datetime.now() - timedelta(days=random.randint(0, 5)),
            'created_by': 'admin',
            'updated_at': datetime.now()
        }
        
        machines_data.append(machine_data)
    
    machine_ids = {}
    for machine_data in machines_data:
        doc_ref = machines_ref.add(machine_data)
        machine_id = doc_ref[1].id
        machine_ids[machine_data['serialNumber']] = machine_id
        print(f"   ✅ Created machine: {machine_data['serialNumber']} - Stage: {machine_data['current_stage']} - User: {machine_data['assigned_username']}")
    
    return machine_ids

def create_machine_history(machine_ids):
    """Create history tracking for completed stages"""
    print("📝 Creating machine history tracking...")
    
    db = get_db()
    history_ref = db.collection('machine_history')
    
    # Create some sample history for a few machines
    sample_machines = list(machine_ids.keys())[:3]  # First 3 machines
    
    for serial_number in sample_machines:
        machine_id = machine_ids[serial_number]
        
        # Create history entries for completed stages
        history_entries = []
        
        if serial_number == 'OLIVIA-001':  # Machine that completed material collection
            history_entries = [
                {
                    'machine_id': machine_id,
                    'machine_serial': serial_number,
                    'stage_name': 'material_collection',
                    'stage_label': 'Collecte des matériaux',
                    'status': 'completed',
                    'assigned_user_id': 'supervisor_user_id',
                    'assigned_username': 'supervisor',
                    'started_at': datetime.now() - timedelta(days=5),
                    'completed_at': datetime.now() - timedelta(days=3),
                    'duration_hours': 4.5,
                    'remarks': 'Matériaux collectés avec succès',
                    'created_at': datetime.now() - timedelta(days=3)
                }
            ]
        elif serial_number == 'OLIVIA-002':  # Machine that completed material + assembly
            history_entries = [
                {
                    'machine_id': machine_id,
                    'machine_serial': serial_number,
                    'stage_name': 'material_collection',
                    'stage_label': 'Collecte des matériaux',
                    'status': 'completed',
                    'assigned_user_id': 'supervisor_user_id',
                    'assigned_username': 'supervisor',
                    'started_at': datetime.now() - timedelta(days=8),
                    'completed_at': datetime.now() - timedelta(days=6),
                    'duration_hours': 4,
                    'remarks': 'Collecte terminée',
                    'created_at': datetime.now() - timedelta(days=6)
                },
                {
                    'machine_id': machine_id,
                    'machine_serial': serial_number,
                    'stage_name': 'assembly',
                    'stage_label': 'Assemblage',
                    'status': 'completed',
                    'assigned_user_id': 'assembly_tech_user_id',
                    'assigned_username': 'assembly_tech',
                    'started_at': datetime.now() - timedelta(days=6),
                    'completed_at': datetime.now() - timedelta(days=2),
                    'duration_hours': 8.5,
                    'remarks': 'Assemblage réalisé avec succès',
                    'created_at': datetime.now() - timedelta(days=2)
                }
            ]
        
        for entry in history_entries:
            history_ref.add(entry)
            print(f"   ✅ Added history: {serial_number} - {entry['stage_label']} ({entry['status']})")

def main():
    """Main restructuring function"""
    print("🚀 Starting complete workflow system restructure...")
    
    # Initialize Firebase
    if not initialize_firebase():
        print("❌ Failed to initialize Firebase!")
        return False
    
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    try:
        # Step 1: Clear all existing data
        clear_all_data()
        
        # Step 2: Create stage definitions
        stage_ids = create_stage_definitions()
        
        # Step 3: Create specialized users
        user_ids = create_specialized_users()
        
        # Step 4: Create realistic clients
        client_ids = create_realistic_clients()
        
        # Step 5: Create simple machines
        machine_ids = create_simple_machines(client_ids, user_ids)
        
        # Step 6: Create machine history
        create_machine_history(machine_ids)
        
        print("\n" + "="*60)
        print("✅ WORKFLOW SYSTEM RESTRUCTURE COMPLETE!")
        print("="*60)
        print(f"📊 Summary:")
        print(f"   • {len(stage_ids)} stage definitions created")
        print(f"   • {len(user_ids)} specialized users created")
        print(f"   • {len(client_ids)} clients created")
        print(f"   • {len(machine_ids)} machines created")
        print(f"   • Machine history tracking enabled")
        print("\n🔑 Test Login Credentials:")
        print("   • admin@isolab.com / admin123 (Admin - all access)")
        print("   • supervisor@isolab.com / super123 (Material Collection)")
        print("   • assembly@isolab.com / tech123 (Assembly)")
        print("   • testing@isolab.com / tech123 (Testing)")
        print("   • delivery@isolab.com / tech123 (Delivery)")
        print("   • installation@isolab.com / tech123 (Installation)")
        print("\n📋 New Structure:")
        print("   • Each user has access to ONE specific stage")
        print("   • Each machine is in ONE current stage")
        print("   • Machine history tracks all completed stages")
        print("   • Simple and trackable workflow")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during restructure: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Ready to update the Python code and blueprints!")
    else:
        print("\n💥 Restructure failed. Please check the errors above.")
