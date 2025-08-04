
"""
Quick script to add test machines to Firestore database
Run this to populate the database with sample machines for testing
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blueprints.firebase_config import initialize_firebase,get_db, is_firebase_available

def add_test_machines():
    """Add sample machines to the database for testing"""
    initialize_firebase()
    
    # Check if database is available
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    db = get_db()
    
    # Sample machine data
    test_machines = [
        {
            'serialNumber': 'OLIVIA-001',
            'machineType': 'Olivia Standard',
            'ficheNumber': 'FT-001',
            'status': 'En cours',
            'prixHT': 25000.0,
            'prixTTC': 30000.0,
            'deliveryDate': (datetime.now() - timedelta(days=30)).isoformat(),
            'installationDate': (datetime.now() - timedelta(days=25)).isoformat(),
            'deliveredBy': 'Mohamed Ali',
            'installedBy': 'Ahmed Ben Salem',
            'paymentType': 'Crédit',
            'paymentStatus': 'En cours',
            'remarques': 'Installation réussie, formation client effectuée',
            'clientId': 'client_001',
            'clientSociety': 'Ferme El Baraka',
            'clientName': 'Karim Hadj Ali',
            'clientPhone': '+216 98 123 456',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-002',
            'machineType': 'Olivia + Broyeur',
            'ficheNumber': 'FT-002',
            'status': 'Terminé',
            'prixHT': 35000.0,
            'prixTTC': 42000.0,
            'deliveryDate': (datetime.now() - timedelta(days=60)).isoformat(),
            'installationDate': (datetime.now() - timedelta(days=55)).isoformat(),
            'deliveredBy': 'Slim Mansouri',
            'installedBy': 'Nizar Trabelsi',
            'paymentType': 'Comptant',
            'paymentStatus': 'Payé',
            'remarques': 'Excellent fonctionnement, client très satisfait',
            'clientId': 'client_002',
            'clientSociety': 'Exploitation Agricole Sidi Bouzid',
            'clientName': 'Fatma Ben Amor',
            'clientPhone': '+216 97 654 321',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-003',
            'machineType': 'Olivia Standard',
            'ficheNumber': 'FT-003',
            'status': 'Problème',
            'prixHT': 28000.0,
            'prixTTC': 33600.0,
            'deliveryDate': (datetime.now() - timedelta(days=15)).isoformat(),
            'installationDate': '',
            'deliveredBy': 'Hedi Bouaziz',
            'installedBy': '',
            'paymentType': 'Crédit',
            'paymentStatus': 'En cours',
            'remarques': 'Problème technique détecté, intervention prévue',
            'clientId': 'client_003',
            'clientSociety': 'Coopérative Agricole Kairouan',
            'clientName': 'Mondher Gasmi',
            'clientPhone': '+216 96 789 123',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-004',
            'machineType': 'Olivia + Broyeur',
            'ficheNumber': 'FT-004',
            'status': 'En cours',
            'prixHT': 32000.0,
            'prixTTC': 38400.0,
            'deliveryDate': (datetime.now() - timedelta(days=10)).isoformat(),
            'installationDate': (datetime.now() - timedelta(days=5)).isoformat(),
            'deliveredBy': 'Tarek Mejri',
            'installedBy': 'Youssef Karray',
            'paymentType': 'Leasing',
            'paymentStatus': 'En cours',
            'remarques': 'Installation en cours, formation prévue demain',
            'clientId': 'client_004',
            'clientSociety': 'Domaine Agricole Sfax',
            'clientName': 'Salma Cherif',
            'clientPhone': '+216 95 456 789',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-005',
            'machineType': 'Olivia Standard',
            'ficheNumber': 'FT-005',
            'status': 'Terminé',
            'prixHT': 26500.0,
            'prixTTC': 31800.0,
            'deliveryDate': (datetime.now() - timedelta(days=45)).isoformat(),
            'installationDate': (datetime.now() - timedelta(days=40)).isoformat(),
            'deliveredBy': 'Rami Jendoubi',
            'installedBy': 'Kamel Ouali',
            'paymentType': 'Comptant',
            'paymentStatus': 'Payé',
            'remarques': 'Machine opérationnelle, maintenance préventive programmée',
            'clientId': 'client_005',
            'clientSociety': 'Ferme Moderne Tunis',
            'clientName': 'Amine Belhadj',
            'clientPhone': '+216 94 321 654',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        }
    ]
    
    try:
        print("🔄 Adding test machines to database...")
        
        for i, machine_data in enumerate(test_machines, 1):
            # Add machine to Firestore
            doc_ref = db.collection('machines').add(machine_data)
            machine_id = doc_ref[1].id
            
            print(f"✅ Added machine {i}/5: {machine_data['serialNumber']} (ID: {machine_id})")
        
        print(f"\n🎉 Successfully added {len(test_machines)} test machines to the database!")
        print("\nMachines added:")
        for machine in test_machines:
            print(f"  • {machine['serialNumber']} - {machine['machineType']} - Status: {machine['status']}")
        
        print("\n💡 You can now test the machines page at /machines/view")
        return True
        
    except Exception as e:
        print(f"❌ Error adding machines: {str(e)}")
        return False

def clear_test_machines():
    """Remove all test machines (optional cleanup function)"""
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    db = get_db()
    
    try:
        print("🔄 Removing test machines...")
        
        # Get all machines with OLIVIA- prefix
        machines_ref = db.collection('machines')
        docs = machines_ref.where('serialNumber', '>=', 'OLIVIA-001').where('serialNumber', '<=', 'OLIVIA-999').stream()
        
        count = 0
        for doc in docs:
            doc.reference.delete()
            count += 1
            print(f"🗑️  Deleted machine: {doc.to_dict().get('serialNumber', 'Unknown')}")
        
        print(f"\n✅ Removed {count} test machines from database")
        return True
        
    except Exception as e:
        print(f"❌ Error removing machines: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Test Machines Database Utility")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_test_machines()
    else:
        add_test_machines()
        print("\n📝 Note: To remove these test machines later, run:")
        print("   python add_test_machines.py clear")
