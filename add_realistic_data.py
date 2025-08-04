"""
Script to add realistic clients and machines based on the actual database structure
This will clear existing test data and add proper data matching the Excel format
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blueprints.firebase_config import initialize_firebase, get_db, is_firebase_available

def clear_all_test_data():
    """Clear all existing test data"""
    initialize_firebase()
    
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    db = get_db()
    
    try:
        print("🔄 Clearing existing test data...")
        
        # Clear machines
        machines_ref = db.collection('machines')
        machines = machines_ref.stream()
        machine_count = 0
        for doc in machines:
            doc.reference.delete()
            machine_count += 1
        
        # Clear clients
        clients_ref = db.collection('clients')
        clients = clients_ref.stream()
        client_count = 0
        for doc in clients:
            doc.reference.delete()
            client_count += 1
        
        print(f"✅ Cleared {machine_count} machines and {client_count} clients")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing data: {str(e)}")
        return False

def add_realistic_clients_and_machines():
    """Add realistic clients and machines based on Excel data structure"""
    initialize_firebase()
    
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    db = get_db()
    
    # Realistic client and machine data based on the Excel structure
    clients_data = [
        {
            'clientCode': '41100611',
            'manager': 'Mohamed Abdellaoui',
            'society': 'Mohamed Abdellaoui',
            'matriculeFiscale': '',
            'phone': '21907382',
            'email': 'hamma.abdellaoui@gmail.com',
            'location': 'Sfax',
            'address': 'Sfax, Tunisie',
            'governorat': 'Sfax',
            'clientType': 'Direct',
            'status': 'Actif',
            'businessSector': 'Agriculture',
            'notes': 'Client particulier',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        },
        {
            'clientCode': '41100621',
            'manager': 'Mohamed Abid',
            'society': 'STE Socap (ste chtourou et Abid de prod. huiles)',
            'matriculeFiscale': '1219290RNM000',
            'phone': '21397599',
            'email': 'socaphuile@yahoo.fr',
            'location': 'Rte Menzel Chaker km5 sfax',
            'address': 'Route Menzel Chaker km5, Sfax',
            'governorat': 'Sfax',
            'clientType': 'Agri',
            'status': 'Actif',
            'businessSector': 'Huilerie',
            'notes': 'Société de production d\'huiles',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        },
        {
            'clientCode': '41100619',
            'manager': 'Thamer Abida',
            'society': 'STE Huilerie Abida',
            'matriculeFiscale': '',
            'phone': '98460467',
            'email': 'abida.huilerie@gmail.com',
            'location': 'Sfax',
            'address': 'Zone industrielle, Sfax',
            'governorat': 'Sfax',
            'clientType': 'Agri',
            'status': 'Actif',
            'businessSector': 'Huilerie',
            'notes': 'Huilerie spécialisée',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        },
        {
            'clientCode': '41100610',
            'manager': 'Hichem Allani',
            'society': 'Allani Group',
            'matriculeFiscale': '',
            'phone': '20829044',
            'email': 'allani.hichem@gmail.com',
            'location': 'Tunis',
            'address': 'Centre ville, Tunis',
            'governorat': 'Tunis',
            'clientType': 'Direct',
            'status': 'Actif',
            'businessSector': 'Agriculture',
            'notes': 'Groupe agricole',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        },
        {
            'clientCode': '41100632',
            'manager': 'Saber Ameri',
            'society': 'S Services Solutions/STE Biomasse Oliviers',
            'matriculeFiscale': '1360829A-1731736k',
            'phone': '50348384',
            'email': 'akreminaceur.1@gmail.com',
            'location': 'Bouhajla Kairouan',
            'address': 'Bouhajla, Kairouan',
            'governorat': 'Kairouan',
            'clientType': 'Leasing',
            'status': 'Actif',
            'businessSector': 'Biomasse',
            'notes': 'Solutions et services biomasse',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        },
        {
            'clientCode': '41100625',
            'manager': 'Ahmed Ben Salem',
            'society': 'Ferme Moderne Ben Salem',
            'matriculeFiscale': '1234567ABC',
            'phone': '22345678',
            'email': 'ahmed.bensalem@ferme.tn',
            'location': 'Monastir',
            'address': 'Route côtière, Monastir',
            'governorat': 'Monastir',
            'clientType': 'Direct',
            'status': 'Actif',
            'businessSector': 'Agriculture',
            'notes': 'Ferme moderne avec équipements avancés',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        },
        {
            'clientCode': '41100630',
            'manager': 'Fatma Karray',
            'society': 'Coopérative Agricole Mahdia',
            'matriculeFiscale': '9876543DEF',
            'phone': '73334455',
            'email': 'coop.mahdia@agriculture.tn',
            'location': 'Mahdia',
            'address': 'Centre Mahdia',
            'governorat': 'Mahdia',
            'clientType': 'Agri',
            'status': 'Actif',
            'businessSector': 'Agriculture',
            'notes': 'Coopérative agricole régionale',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        },
        {
            'clientCode': '41100635',
            'manager': 'Noureddine Trabelsi',
            'society': 'Exploitation Trabelsi & Fils',
            'matriculeFiscale': '5555444GHI',
            'phone': '95123456',
            'email': 'trabelsi.exploitation@gmail.com',
            'location': 'Sousse',
            'address': 'Zone rurale, Sousse',
            'governorat': 'Sousse',
            'clientType': 'Direct',
            'status': 'Actif',
            'businessSector': 'Agriculture',
            'notes': 'Exploitation familiale',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        },
        {
            'clientCode': '41100640',
            'manager': 'Monia Hammami',
            'society': 'Domaine Hammami',
            'matriculeFiscale': '3333222JKL',
            'phone': '98765432',
            'email': 'monia.hammami@domaine.tn',
            'location': 'Nabeul',
            'address': 'Domaine agricole, Nabeul',
            'governorat': 'Nabeul',
            'clientType': 'Leasing',
            'status': 'Actif',
            'businessSector': 'Horticulture',
            'notes': 'Domaine spécialisé en horticulture',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        },
        {
            'clientCode': '41100645',
            'manager': 'Karim Jendoubi',
            'society': 'Ferme Bio Jendoubi',
            'matriculeFiscale': '7777888MNO',
            'phone': '24567890',
            'email': 'karim.jendoubi@biofarm.tn',
            'location': 'Béja',
            'address': 'Zone agricole, Béja',
            'governorat': 'Béja',
            'clientType': 'Direct',
            'status': 'Actif',
            'businessSector': 'Agriculture Bio',
            'notes': 'Agriculture biologique certifiée',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now(),
            'machines': []
        }
    ]
    
    # Machine data with proper associations
    machines_data = [
        {
            'serialNumber': 'OLIVIA-001',
            'machineType': 'Olivia Standard',
            'ficheNumber': 'FT-001',
            'status': 'En cours',
            'prixHT': 105000.0,
            'prixTTC': 0.0,  # Sans broyeur
            'deliveryDate': '',
            'installationDate': '',
            'deliveredBy': '',
            'installedBy': '',
            'paymentType': 'Crédit',
            'paymentStatus': 'En cours',
            'confirmation': 'En attente',
            'facturation': 'Non facturée',
            'commentairesPaiement': 'En cours de traitement',
            'itpStatus': 'Non',
            'remarques': 'Machine commandée, en attente de livraison',
            'clientCode': '41100611',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': '91913613',
            'machineType': 'Olivia Standard',
            'ficheNumber': 'FT-002',
            'status': 'Terminé',
            'prixHT': 105000.0,
            'prixTTC': 105000.0,
            'deliveryDate': '2023-10-04',
            'installationDate': '2023-10-04',
            'deliveredBy': 'Oussema',
            'installedBy': 'Oussema',
            'paymentType': 'Chèques multiples',
            'paymentStatus': 'Payé',
            'confirmation': 'Livré par Oussema le 04/10/2023',
            'facturation': 'Facturée (reste décharge)',
            'commentairesPaiement': 'Totalité payée +RS (avance chq 55k+ chq 18k950 +chq 15k+ chq 15k)',
            'itpStatus': 'Décharge ITP reçu',
            'remarques': 'Installation terminée, client satisfait',
            'clientCode': '41100621',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': '91911130',
            'machineType': 'Olivia + Broyeur',
            'ficheNumber': 'FT-003',
            'status': 'Terminé',
            'prixHT': 110000.0,
            'prixTTC': 115000.0,
            'deliveryDate': '2023-11-15',
            'installationDate': '2023-11-16',
            'deliveredBy': 'Oussema',
            'installedBy': 'Oussema',
            'paymentType': 'Chèque',
            'paymentStatus': 'Payé',
            'confirmation': 'Olivia livré + broyeur livré',
            'facturation': 'Facturée',
            'commentairesPaiement': 'Paiement totalité chèque versable 110 HT+ chèque 3850 dt versable+ RS reçue',
            'itpStatus': 'Non',
            'remarques': 'Machine avec broyeur, installation réussie',
            'clientCode': '41100619',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-004',
            'machineType': 'Olivia Standard',
            'ficheNumber': 'FT-004',
            'status': 'En cours',
            'prixHT': 105000.0,
            'prixTTC': 0.0,
            'deliveryDate': '',
            'installationDate': '',
            'deliveredBy': '',
            'installedBy': '',
            'paymentType': 'Crédit',
            'paymentStatus': 'En cours',
            'confirmation': 'Commande confirmée',
            'facturation': 'Non facturée',
            'commentairesPaiement': 'Dossier en cours',
            'itpStatus': 'Non',
            'remarques': 'Commande en cours de traitement',
            'clientCode': '41100610',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': '91918438',
            'machineType': 'Olivia + Broyeur',
            'ficheNumber': 'FT-005',
            'status': 'Terminé',
            'prixHT': 110000.0,
            'prixTTC': 117701.0,
            'deliveryDate': '2023-12-08',
            'installationDate': '2023-12-08',
            'deliveredBy': 'Oussema',
            'installedBy': 'Oussema',
            'paymentType': 'Leasing',
            'paymentStatus': 'En cours',
            'confirmation': 'Olivia + broyeur livrés le 8/12/2023',
            'facturation': 'En cours',
            'commentairesPaiement': 'Chq de garantie 117701ttc en attente du leasing',
            'itpStatus': 'Non',
            'remarques': 'Livraison effectuée, leasing en cours',
            'clientCode': '41100632',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-006',
            'machineType': 'Olivia Standard',
            'ficheNumber': 'FT-006',
            'status': 'En cours',
            'prixHT': 105000.0,
            'prixTTC': 126000.0,
            'deliveryDate': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
            'installationDate': (datetime.now() - timedelta(days=12)).strftime('%Y-%m-%d'),
            'deliveredBy': 'Mohamed Ali',
            'installedBy': 'Ahmed',
            'paymentType': 'Comptant',
            'paymentStatus': 'Payé',
            'confirmation': 'Livraison confirmée',
            'facturation': 'Facturée',
            'commentairesPaiement': 'Paiement intégral reçu',
            'itpStatus': 'Oui',
            'remarques': 'Installation réussie, formation effectuée',
            'clientCode': '41100625',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-007',
            'machineType': 'Olivia + Broyeur',
            'ficheNumber': 'FT-007',
            'status': 'Terminé',
            'prixHT': 110000.0,
            'prixTTC': 132000.0,
            'deliveryDate': (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d'),
            'installationDate': (datetime.now() - timedelta(days=42)).strftime('%Y-%m-%d'),
            'deliveredBy': 'Tarek',
            'installedBy': 'Youssef',
            'paymentType': 'Crédit',
            'paymentStatus': 'Payé',
            'confirmation': 'Installation terminée',
            'facturation': 'Facturée',
            'commentairesPaiement': 'Paiement échelonné terminé',
            'itpStatus': 'Oui',
            'remarques': 'Excellent fonctionnement, client très satisfait',
            'clientCode': '41100630',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-008',
            'machineType': 'Olivia Standard',
            'ficheNumber': 'FT-008',
            'status': 'Problème',
            'prixHT': 105000.0,
            'prixTTC': 126000.0,
            'deliveryDate': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d'),
            'installationDate': '',
            'deliveredBy': 'Slim',
            'installedBy': '',
            'paymentType': 'Comptant',
            'paymentStatus': 'Payé',
            'confirmation': 'Livré mais problème technique',
            'facturation': 'Facturée',
            'commentairesPaiement': 'Paiement reçu',
            'itpStatus': 'En attente',
            'remarques': 'Problème technique détecté, intervention programmée',
            'clientCode': '41100635',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-009',
            'machineType': 'Olivia + Broyeur',
            'ficheNumber': 'FT-009',
            'status': 'En cours',
            'prixHT': 110000.0,
            'prixTTC': 132000.0,
            'deliveryDate': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'installationDate': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'deliveredBy': 'Nizar',
            'installedBy': 'Kamel',
            'paymentType': 'Leasing',
            'paymentStatus': 'En cours',
            'confirmation': 'Installation en cours',
            'facturation': 'En cours',
            'commentairesPaiement': 'Dossier leasing approuvé',
            'itpStatus': 'Non',
            'remarques': 'Installation en cours, formation prévue',
            'clientCode': '41100640',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        },
        {
            'serialNumber': 'OLIVIA-010',
            'machineType': 'Olivia Standard',
            'ficheNumber': 'FT-010',
            'status': 'Terminé',
            'prixHT': 105000.0,
            'prixTTC': 126000.0,
            'deliveryDate': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
            'installationDate': (datetime.now() - timedelta(days=58)).strftime('%Y-%m-%d'),
            'deliveredBy': 'Rami',
            'installedBy': 'Oussema',
            'paymentType': 'Comptant',
            'paymentStatus': 'Payé',
            'confirmation': 'Installation terminée avec succès',
            'facturation': 'Facturée',
            'commentairesPaiement': 'Paiement intégral reçu, RS OK',
            'itpStatus': 'Oui',
            'remarques': 'Machine opérationnelle, maintenance préventive programmée',
            'clientCode': '41100645',
            'created_by': 'admin',
            'dateAdded': datetime.now(),
            'dateUpdated': datetime.now()
        }
    ]
    
    try:
        print("🔄 Adding realistic clients and machines...")
        
        # Add clients first
        client_ids = {}
        for i, client_data in enumerate(clients_data, 1):
            doc_ref = db.collection('clients').add(client_data)
            client_id = doc_ref[1].id
            client_ids[client_data['clientCode']] = client_id
            
            print(f"✅ Added client {i}/10: {client_data['society']} (Code: {client_data['clientCode']})")
        
        # Add machines with client references
        for i, machine_data in enumerate(machines_data, 1):
            # Find the corresponding client
            client_code = machine_data['clientCode']
            if client_code in client_ids:
                # Update machine data with actual client info
                client_id = client_ids[client_code]
                client_info = next(c for c in clients_data if c['clientCode'] == client_code)
                
                machine_data.update({
                    'clientId': client_id,
                    'clientSociety': client_info['society'],
                    'clientName': client_info['manager'],
                    'clientPhone': client_info['phone'],
                    'clientEmail': client_info.get('email', ''),
                    'clientLocation': client_info['location'],
                    'clientAddress': client_info['address']
                })
                
                # Remove clientCode as it's now replaced with clientId
                del machine_data['clientCode']
                
                # Add machine to Firestore
                doc_ref = db.collection('machines').add(machine_data)
                machine_id = doc_ref[1].id
                
                # Update client's machines list
                client_ref = db.collection('clients').document(client_id)
                client_doc = client_ref.get()
                if client_doc.exists:
                    current_machines = client_doc.to_dict().get('machines', [])
                    current_machines.append(machine_data['serialNumber'])
                    client_ref.update({'machines': current_machines})
                
                print(f"✅ Added machine {i}/10: {machine_data['serialNumber']} for {client_info['society']}")
        
        print(f"\n🎉 Successfully added {len(clients_data)} clients and {len(machines_data)} machines!")
        print("\n📊 Summary:")
        print("Clients by type:")
        direct_count = sum(1 for c in clients_data if c['clientType'] == 'Direct')
        agri_count = sum(1 for c in clients_data if c['clientType'] == 'Agri')
        leasing_count = sum(1 for c in clients_data if c['clientType'] == 'Leasing')
        print(f"  • Direct: {direct_count}")
        print(f"  • Agri: {agri_count}")
        print(f"  • Leasing: {leasing_count}")
        
        print("\nMachines by status:")
        en_cours = sum(1 for m in machines_data if m['status'] == 'En cours')
        termine = sum(1 for m in machines_data if m['status'] == 'Terminé')
        probleme = sum(1 for m in machines_data if m['status'] == 'Problème')
        print(f"  • En cours: {en_cours}")
        print(f"  • Terminé: {termine}")
        print(f"  • Problème: {probleme}")
        
        print("\n💡 You can now test the application with realistic data!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding data: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Realistic Data Setup Utility")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_all_test_data()
    else:
        # Clear old data first, then add new data
        print("🔄 Step 1: Clearing old test data...")
        clear_all_test_data()
        
        print("\n🔄 Step 2: Adding realistic data...")
        add_realistic_clients_and_machines()
        
        print("\n📝 Note: To clear this data later, run:")
        print("   python add_realistic_data.py clear")
