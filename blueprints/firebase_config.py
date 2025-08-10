"""
Firebase configuration and initialization module
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os


db = None
firebase_app = None

def initialize_firebase():
    """Initialize Firebase Admin SDK and Firestore"""
    global db, firebase_app
    
    try:
        # Check for service account key - use forward slashes for cross-platform compatibility
        service_key_path = "config/isolab-support-firebase-adminsdk-fbsvc-7a36653eaf.json"
        
        print(f"🔍 DEBUG: Looking for Firebase service key at: {service_key_path}")
        print(f"🔍 DEBUG: Current working directory: {os.getcwd()}")
        print(f"🔍 DEBUG: File exists check: {os.path.exists(service_key_path)}")

        if not os.path.exists(service_key_path):
            print(f"❌ DEBUG: Firebase service account key not found at {service_key_path}")
            
            # Try alternative paths
            alternative_paths = [
                "/app/config/isolab-support-firebase-adminsdk-fbsvc-7a36653eaf.json",
                "./config/isolab-support-firebase-adminsdk-fbsvc-7a36653eaf.json",
                "config\\isolab-support-firebase-adminsdk-fbsvc-7a36653eaf.json"
            ]
            
            for alt_path in alternative_paths:
                print(f"🔍 DEBUG: Trying alternative path: {alt_path}")
                if os.path.exists(alt_path):
                    service_key_path = alt_path
                    print(f"✅ DEBUG: Found Firebase key at: {service_key_path}")
                    break
            else:
                print("❌ DEBUG: Firebase service account key not found in any location")
                print("Some features may not work. Please check FIREBASE_SETUP.md for configuration instructions.")
                return False
        
        # Initialize Firebase
        print(f"🔍 DEBUG: Initializing Firebase with service key: {service_key_path}")
        cred = credentials.Certificate(service_key_path)
        firebase_app = firebase_admin.initialize_app(cred)
        print("✅ DEBUG: Firebase app initialized successfully")
        
        # Initialize Firestore DB
        db = firestore.client()
        print("✅ DEBUG: Firestore client initialized successfully")
        
        print("✅ DEBUG: Firebase initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Firebase initialization failed: {e}")
        print(f"❌ DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        return False

def get_db():
    """Get Firestore database instance"""
    return db

def is_firebase_available():
    """Check if Firebase is properly initialized"""
    return db is not None
