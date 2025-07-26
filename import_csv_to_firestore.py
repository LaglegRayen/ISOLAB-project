#!/usr/bin/env python3
"""
📦 Script to import data from CSV files into Firestore
Supports importing users, clients, and machines with workflow stages

Usage: 
  python import_csv_to_firestore.py users <users_csv_file>
  python import_csv_to_firestore.py machines <machines_csv_file>
  python import_csv_to_firestore.py auto <csv_file>  # Auto-detect content
"""

import sys
import csv
import os
from datetime import datetime
import re

# Import Firebase configuration
from blueprints.firebase_config import initialize_firebase, get_db, is_firebase_available
from blueprints.users import ROLES, DEFAULT_STAGES


class CSVToFirestoreImporter:
    def __init__(self):
        self.db = None
        self.users_imported = 0
        self.clients_imported = 0
        self.machines_imported = 0
        self.stages_created = 0
        self.errors = []
        
    def initialize(self):
        """Initialize Firebase connection"""
        print("Initializing Firebase connection...")
        if not initialize_firebase():
            print("❌ Failed to initialize Firebase. Please check your serviceAccountKey.json")
            return False
        
        self.db = get_db()
        if not is_firebase_available():
            print("Firebase is not available")
            return False

        print("Firebase initialized successfully")
        return True
    
    def detect_row_type(self, row):
        """
        Detect if a row contains user, client or machine data
        Returns: 'user', 'client', 'machine', or 'unknown'
        """
        if not row or all(not cell.strip() for cell in row):
            return 'unknown'
        
        # Convert row to lowercase for detection
        row_str = ' '.join(str(cell).lower() for cell in row)
        
        # User indicators (check first as they're most specific)
        user_indicators = [
            'admin', 'operator', 'technician', 'manager', 'staff',
            'material_operator', 'assembly_technician', 'delivery_manager', 'maintenance_staff'
        ]
        
        # Machine indicators
        machine_indicators = [
            'olivia', 'broyeur', 'tracteur', 'machine', 
            'série', 'serial', 'model', 'marque',
            '91', 'ht', 'ttc', 'prix'  # Serial numbers often start with 91
        ]
        
        # Client indicators  
        client_indicators = [
            'sté', 'société', 'huilerie', 'lease', 'bank',
            'plc', 'sarl', 'matricule', 'fiscal', '@'
        ]
        
        # Count indicators
        user_score = sum(1 for indicator in user_indicators if indicator in row_str)
        machine_score = sum(1 for indicator in machine_indicators if indicator in row_str)
        client_score = sum(1 for indicator in client_indicators if indicator in row_str)
        
        # Additional specific checks
        for cell in row:
            cell_str = str(cell).strip()
            
            # Check for role patterns
            if cell_str.lower() in ROLES:
                user_score += 5
            
            # Check for serial number pattern (numbers starting with 91)
            if re.match(r'^91\d{6,}$', cell_str):
                machine_score += 3
            
            # Check for email pattern
            if '@' in cell_str and '.' in cell_str:
                # Could be user or client
                if any(role in row_str for role in ROLES.keys()):
                    user_score += 2
                else:
                    client_score += 2
            
            # Check for phone number pattern
            if re.match(r'^[\d\s\-\+\/]{8,}$', cell_str):
                if len(cell_str.replace(' ', '').replace('-', '').replace('+', '').replace('/', '')) >= 8:
                    client_score += 1
        
        # Determine type based on scores
        if user_score > machine_score and user_score > client_score:
            return 'user'
        elif machine_score > client_score:
            return 'machine'
        elif client_score > 0:
            return 'client'
        else:
            return 'unknown'
    
    def clean_and_validate_user_data(self, row):
        """
        Extract and validate user data from a CSV row
        Returns: dict with user data or None if invalid
        """
        try:
            # Common user field patterns
            user_data = {
                'name': '',
                'email': '',
                'role': '',
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
            
            # Extract data from row (flexible approach)
            non_empty_cells = [str(cell).strip() for cell in row if str(cell).strip()]
            
            if len(non_empty_cells) < 3:
                return None
            
            # Try to identify fields
            for cell in non_empty_cells:
                cell_str = str(cell).strip()
                
                # Role detection (highest priority)
                if cell_str.lower() in ROLES:
                    user_data['role'] = cell_str.lower()
                
                # Email detection
                elif '@' in cell_str and '.' in cell_str:
                    user_data['email'] = cell_str
                
                # Name detection (if not email or role)
                elif not user_data['name'] and '@' not in cell_str and cell_str.lower() not in ROLES:
                    user_data['name'] = cell_str
            
            # Fallback: assume order is name, email, role
            if not user_data['name'] and non_empty_cells:
                user_data['name'] = non_empty_cells[0]
            
            if not user_data['email'] and len(non_empty_cells) > 1:
                potential_email = non_empty_cells[1]
                if '@' in potential_email:
                    user_data['email'] = potential_email
            
            if not user_data['role'] and len(non_empty_cells) > 2:
                potential_role = non_empty_cells[2].lower()
                if potential_role in ROLES:
                    user_data['role'] = potential_role
            
            # Validation: require name, email, and valid role
            if not user_data['name'] or not user_data['email'] or not user_data['role']:
                return None
            
            if user_data['role'] not in ROLES:
                return None
            
            # Clean up empty fields
            return {k: v for k, v in user_data.items() if v}
            
        except Exception as e:
            print(f"⚠️ Error processing user row: {e}")
            return None
    
    def clean_and_validate_client_data(self, row):
        """
        Extract and validate client data from a CSV row
        Returns: dict with client data or None if invalid
        """
        try:
            # Common client field patterns
            client_data = {
                'nom': '',
                'prenom': '',
                'telephone': '',
                'adresse': '',
                'type': '',
                'location': '',
                'status': 'actif',
                'created_at': datetime.now().isoformat()
            }
            
            # Extract data from row (flexible approach)
            non_empty_cells = [str(cell).strip() for cell in row if str(cell).strip()]
            
            if len(non_empty_cells) < 2:
                return None
            
            # Try to identify fields
            for cell in non_empty_cells:
                cell_str = str(cell).strip()
                
                # Phone number detection
                if re.match(r'^[\d\s\-\+\/]{8,}$', cell_str):
                    if len(cell_str.replace(' ', '').replace('-', '').replace('+', '').replace('/', '')) >= 8:
                        client_data['telephone'] = cell_str
                
                # Email detection
                elif '@' in cell_str and '.' in cell_str:
                    client_data['email'] = cell_str
                
                # Type detection
                elif any(t in cell_str.lower() for t in ['leasing', 'direct', 'agri']):
                    client_data['type'] = cell_str
                
                # Location detection (common Tunisian cities)
                elif any(city in cell_str.lower() for city in ['sfax', 'tunis', 'sousse', 'kairouan', 'bizerte', 'monastir', 'sidi bouzid']):
                    client_data['location'] = cell_str
                
                # Society name (usually longer text with keywords)
                elif any(word in cell_str.lower() for word in ['sté', 'société', 'huilerie', 'bank', 'plc', 'sarl']):
                    if not client_data['nom']:
                        client_data['nom'] = cell_str
                
                # Manager name (if société already found)
                elif client_data['nom'] and not client_data['prenom'] and len(cell_str) > 2:
                    # Likely a person's name
                    if not any(char.isdigit() for char in cell_str):
                        client_data['prenom'] = cell_str
                
                # Address (longer text without specific patterns)
                elif len(cell_str) > 10 and not client_data['adresse']:
                    if not any(pattern in cell_str.lower() for pattern in ['sté', '@', 'leasing']):
                        client_data['adresse'] = cell_str
            
            # Fallback: use first few cells if pattern matching failed
            if not client_data['nom'] and non_empty_cells:
                client_data['nom'] = non_empty_cells[0]
            
            if not client_data['prenom'] and len(non_empty_cells) > 1:
                client_data['prenom'] = non_empty_cells[1]
            
            if not client_data['telephone'] and len(non_empty_cells) > 2:
                # Check if third cell could be a phone
                potential_phone = non_empty_cells[2]
                if any(char.isdigit() for char in potential_phone):
                    client_data['telephone'] = potential_phone
            
            # Validation: require at least name and phone
            if not client_data['nom'] or not client_data['telephone']:
                return None
            
            # Clean up empty fields
            return {k: v for k, v in client_data.items() if v}
            
        except Exception as e:
            print(f"⚠️ Error processing client row: {e}")
            return None
    
    def get_users_by_role(self, role):
        """Helper function to get users by role"""
        try:
            users_ref = self.db.collection('users')
            users = users_ref.where('role', '==', role).where('status', '==', 'active').get()
            
            return [{'id': doc.id, **doc.to_dict()} for doc in users]
            
        except Exception as e:
            print(f"Error getting users by role: {e}")
            return []
    
    def create_stages_for_machine(self, machine_id):
        """Create default stages for a machine with user assignments"""
        try:
            # Get machine document
            machine_ref = self.db.collection('machines').document(machine_id)
            machine_doc = machine_ref.get()
            
            if not machine_doc.exists:
                return False
            
            # Create stages subcollection
            stages_ref = machine_ref.collection('stages')
            
            for stage_template in DEFAULT_STAGES:
                # Get users with this role
                role_users = self.get_users_by_role(stage_template['role'])
                
                if role_users:
                    # Randomly assign a user with the matching role
                    import random
                    assigned_user = random.choice(role_users)
                    responsible_user_id = assigned_user['id']
                else:
                    responsible_user_id = None
                    print(f"⚠️ No users found for role: {stage_template['role']}")
                
                stage_data = {
                    'name': stage_template['name'],
                    'label': stage_template['label'],
                    'role': stage_template['role'],
                    'order': stage_template['order'],
                    'status': 'in_progress' if stage_template['order'] == 1 else 'pending',
                    'responsible_user_id': responsible_user_id,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                
                stages_ref.add(stage_data)
                self.stages_created += 1
            
            return True
            
        except Exception as e:
            print(f"Error creating stages: {e}")
            return False
    
    def clean_and_validate_machine_data(self, row):
        """
        Extract and validate machine data from a CSV row
        Returns: dict with machine data or None if invalid
        """
        try:
            # Common machine field patterns
            machine_data = {
                'serialNumber': '',
                'machineType': '',
                'marque': '',
                'modele': '',
                'puissance': '',
                'status': 'actif',
                'clientId': '',
                'created_at': datetime.now().isoformat()
            }
            
            # Extract data from row
            non_empty_cells = [str(cell).strip() for cell in row if str(cell).strip()]
            
            if len(non_empty_cells) < 2:
                return None
            
            # Try to identify fields
            for cell in non_empty_cells:
                cell_str = str(cell).strip()
                
                # Serial number detection (numbers starting with 91)
                if re.match(r'^91\d{6,}$', cell_str):
                    machine_data['serialNumber'] = cell_str
                
                # Machine type detection
                elif any(t in cell_str.lower() for t in ['olivia', 'broyeur', 'tracteur']):
                    machine_data['machineType'] = cell_str
                
                # Brand detection
                elif any(brand in cell_str.lower() for brand in ['john deere', 'case', 'new holland', 'fendt']):
                    machine_data['marque'] = cell_str
                
                # Price detection
                elif any(price_indicator in cell_str.lower() for price_indicator in ['dt', 'eur', 'usd']) and any(char.isdigit() for char in cell_str):
                    if 'ht' in cell_str.lower():
                        try:
                            machine_data['prixHT'] = float(re.sub(r'[^\d.]', '', cell_str))
                        except:
                            pass
                    elif 'ttc' in cell_str.lower():
                        try:
                            machine_data['prixTTC'] = float(re.sub(r'[^\d.]', '', cell_str))
                        except:
                            pass
                
                # Status detection
                elif any(status in cell_str.lower() for status in ['actif', 'maintenance', 'inactive']):
                    machine_data['status'] = cell_str.lower()
            
            # Fallback: use first cell as serial if no serial found
            if not machine_data['serialNumber'] and non_empty_cells:
                # Check if first cell could be a serial
                first_cell = non_empty_cells[0]
                if any(char.isdigit() for char in first_cell) and len(first_cell) >= 5:
                    machine_data['serialNumber'] = first_cell
            
            # Fallback: use second cell as type if no type found
            if not machine_data['machineType'] and len(non_empty_cells) > 1:
                machine_data['machineType'] = non_empty_cells[1]
            
            # Validation: require at least serial number
            if not machine_data['serialNumber']:
                return None
            
            # Clean up empty fields
            return {k: v for k, v in machine_data.items() if v}
            
        except Exception as e:
            print(f"⚠️ Error processing machine row: {e}")
            return None
    
    def import_csv_file(self, csv_file_path, import_type='auto'):
        """Import data from CSV file to Firestore"""
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV file not found: {csv_file_path}")
            return False
        
        print(f"📄 Reading CSV file: {csv_file_path}")
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                
                # Skip header row if it exists
                first_row = next(reader, None)
                if first_row and import_type == 'users':
                    # Check if it's a header row
                    if first_row[0].lower() in ['name', 'nom', 'user']:
                        pass  # Skip header
                    else:
                        # Process first row as data
                        file.seek(0)
                        reader = csv.reader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Skip empty rows
                        if not row or all(not cell.strip() for cell in row):
                            continue
                        
                        # Detect or use specified import type
                        if import_type == 'auto':
                            row_type = self.detect_row_type(row)
                        elif import_type == 'users':
                            row_type = 'user'
                        elif import_type == 'machines':
                            row_type = self.detect_row_type(row)  # Still detect between client/machine
                        else:
                            row_type = import_type
                        
                        if row_type == 'user':
                            user_data = self.clean_and_validate_user_data(row)
                            if user_data:
                                # Check if user already exists
                                existing_users = self.db.collection('users').where('email', '==', user_data['email']).get()
                                if existing_users:
                                    print(f"⚠️ User already exists: {user_data['email']} (Row {row_num})")
                                else:
                                    # Add to Firestore
                                    doc_ref = self.db.collection('users').add(user_data)
                                    self.users_imported += 1
                                    print(f"✅ User imported: {user_data.get('name', 'Unknown')} ({user_data.get('role', 'No role')}) (Row {row_num})")
                            else:
                                self.errors.append(f"Row {row_num}: Invalid user data")
                        
                        elif row_type == 'client':
                            client_data = self.clean_and_validate_client_data(row)
                            if client_data:
                                # Add to Firestore
                                doc_ref = self.db.collection('clients').add(client_data)
                                self.clients_imported += 1
                                print(f"✅ Client imported: {client_data.get('nom', 'Unknown')} (Row {row_num})")
                            else:
                                self.errors.append(f"Row {row_num}: Invalid client data")
                        
                        elif row_type == 'machine':
                            machine_data = self.clean_and_validate_machine_data(row)
                            if machine_data:
                                # Add to Firestore
                                doc_ref = self.db.collection('machines').add(machine_data)
                                machine_id = doc_ref[1].id
                                self.machines_imported += 1
                                
                                # Create workflow stages for the machine
                                stages_created = self.create_stages_for_machine(machine_id)
                                
                                print(f"✅ Machine imported: {machine_data.get('serialNumber', 'Unknown')} (Row {row_num})")
                                if stages_created:
                                    print(f"   📋 Workflow stages created for machine")
                            else:
                                self.errors.append(f"Row {row_num}: Invalid machine data")
                        
                        else:
                            self.errors.append(f"Row {row_num}: Could not determine data type")
                    
                    except Exception as e:
                        self.errors.append(f"Row {row_num}: {str(e)}")
                        print(f"⚠️ Error processing row {row_num}: {e}")
        
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
            return False
        
        return True
    
    def print_summary(self):
        """Print import summary"""
        print("\n" + "="*50)
        print("📊 IMPORT SUMMARY")
        print("="*50)
        print(f"✅ Users imported: {self.users_imported}")
        print(f"✅ Clients imported: {self.clients_imported}")
        print(f"✅ Machines imported: {self.machines_imported}")
        print(f"📋 Workflow stages created: {self.stages_created}")
        print(f"⚠️ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n🚨 Errors encountered:")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
        
        print("="*50)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python import_csv_to_firestore.py users <users_csv_file>")
        print("  python import_csv_to_firestore.py machines <machines_csv_file>")
        print("  python import_csv_to_firestore.py auto <csv_file>")
        print("\nExamples:")
        print("  python import_csv_to_firestore.py users data/users.csv")
        print("  python import_csv_to_firestore.py machines data/machines.csv")
        print("  python import_csv_to_firestore.py auto data/mixed_data.csv")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Old format: assume auto-detect
        import_type = 'auto'
        csv_file_path = sys.argv[1]
    else:
        # New format: specify type
        import_type = sys.argv[1].lower()
        csv_file_path = sys.argv[2]
        
        if import_type not in ['users', 'machines', 'auto']:
            print("❌ Invalid import type. Use: users, machines, or auto")
            sys.exit(1)
    
    # Initialize importer
    importer = CSVToFirestoreImporter()
    
    # Initialize Firebase
    if not importer.initialize():
        sys.exit(1)
    
    print(f"\n🚀 Starting {import_type} import from: {csv_file_path}")
    
    if import_type == 'users':
        print("👥 Importing users...")
    elif import_type == 'machines':
        print("🔍 Auto-detecting client and machine data...")
        print("📋 Creating workflow stages for machines...")
    else:
        print("🔍 Auto-detecting users, clients, and machine data...")
    
    # Import data
    success = importer.import_csv_file(csv_file_path, import_type)
    
    # Print summary
    importer.print_summary()
    
    if success:
        print("\n🎉 Import completed successfully!")
        if import_type == 'users':
            print("\n💡 Next steps:")
            print("  1. Import your machines: python import_csv_to_firestore.py machines data/machines.csv")
            print("  2. Users will be automatically assigned to machine workflow stages")
    else:
        print("\n❌ Import failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
