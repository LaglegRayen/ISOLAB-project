#!/usr/bin/env python3
"""
Fix user passwords
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blueprints.firebase_config import initialize_firebase, get_db, is_firebase_available
import hashlib

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def fix_passwords():
    """Fix user passwords"""
    print("🔑 Fixing user passwords...")
    
    # Initialize Firebase
    if not initialize_firebase():
        print("❌ Failed to initialize Firebase!")
        return False
    
    if not is_firebase_available():
        print("❌ Firebase database is not available!")
        return False
    
    db = get_db()
    users_ref = db.collection('users')
    
    # Get all users
    users_docs = users_ref.stream()
    
    password_updates = {
        'supervisor': 'super123',
        'admin': 'admin123',
        'assembly_tech': 'tech123',
        'testing_tech': 'tech123',
        'delivery_tech': 'tech123',
        'installation_tech': 'tech123'
    }
    
    for doc in users_docs:
        user_data = doc.to_dict()
        username = user_data.get('username')
        
        if username in password_updates:
            new_password = password_updates[username]
            hashed_password = hash_password(new_password)
            
            # Update the password
            doc.reference.update({'password': hashed_password})
            print(f"   ✅ Updated password for {username}")
    
    return True

if __name__ == "__main__":
    fix_passwords()
