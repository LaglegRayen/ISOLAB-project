import firebase_admin
from firebase_admin import credentials, firestore
import random
import uuid
from firebase_admin import credentials, firestore, initialize_app

# 🔑 Path to your service account key JSON
cred = credentials.Certificate("C:\\Users\\rima lagleg\\Desktop\\ML DL\\ISOLAB-project\\config\\isolab-agri-support-firebase-adminsdk-fbsvc-73184d48a6.json")

initialize_app(cred)
db = firestore.client()

# Define roles and stages
ROLES = {
    'material_operator': {
        'name': 'Opérateur Matériaux',
        'stages': ['material_collection'],
        'level': 1
    },
    'assembly_technician': {
        'name': 'Technicien Assemblage',
        'stages': ['assembly', 'testing'],
        'level': 2
    },
    'delivery_manager': {
        'name': 'Responsable Livraison',
        'stages': ['delivery', 'installation'],
        'level': 3
    },
    'maintenance_staff': {
        'name': 'Service Maintenance',
        'stages': ['maintenance', 'follow_up'],
        'level': 2
    },
    'admin': {
        'name': 'Administrateur',
        'stages': ['material_collection', 'assembly', 'testing', 'delivery', 'installation', 'maintenance', 'follow_up'],
        'level': 5
    }
}

DEFAULT_STAGES = [
    {
        'name': 'material_collection',
        'label': 'Collecte des matériaux',
        'role': 'material_operator',
        'order': 1,
        'status': 'pending'
    },
    {
        'name': 'assembly',
        'label': 'Assemblage',
        'role': 'assembly_technician',
        'order': 2,
        'status': 'pending'
    },
    {
        'name': 'testing',
        'label': 'Tests et contrôle qualité',
        'role': 'assembly_technician',
        'order': 3,
        'status': 'pending'
    },
    {
        'name': 'delivery',
        'label': 'Livraison',
        'role': 'delivery_manager',
        'order': 4,
        'status': 'pending'
    },
    {
        'name': 'installation',
        'label': 'Installation',
        'role': 'delivery_manager',
        'order': 5,
        'status': 'pending'
    }
]

# 1. Seed roles
roles_ref = db.collection('roles')
for role_key, role_data in ROLES.items():
    roles_ref.document(role_key).set(role_data)

print("✅ Roles added.")

# 2. Seed workflow stages
stages_ref = db.collection('workflow_stages')
for stage in DEFAULT_STAGES:
    stages_ref.document(stage['name']).set(stage)

print("✅ Workflow stages added.")

# 3. Create users for each role
users_ref = db.collection('users')
user_ids_by_role = {}

for i, (role_key, role_data) in enumerate(ROLES.items(), start=1):
    user_id = str(uuid.uuid4())
    user_data = {
        'name': f'User {i}',
        'email': f'user{i}@example.com',
        'role': role_key
    }
    users_ref.document(user_id).set(user_data)
    user_ids_by_role[role_key] = user_id  # Store for later use in assigning workflow instances

print("✅ Users added.")

# 4. Create workflow_instances assigned to appropriate users
workflow_ref = db.collection('workflow_instances')
for workflow_index in range(3):  # Create 3 workflows
    workflow_id = f'workflow_{workflow_index + 1}'
    for stage in DEFAULT_STAGES:
        role = stage['role']
        assigned_user_id = user_ids_by_role.get(role)
        instance_id = str(uuid.uuid4())
        workflow_ref.document(instance_id).set({
            'workflow_id': workflow_id,
            'stage': stage['name'],
            'label': stage['label'],
            'assigned_user': assigned_user_id,
            'assigned_role': role,
            'status': random.choice(['pending', 'in_progress', 'completed']),
            'order': stage['order']
        })

print("✅ Workflow instances created and assigned to users.")
