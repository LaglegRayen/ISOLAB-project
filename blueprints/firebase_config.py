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
        # Check for service account key
        service_key_path = "C:\\Users\\rima lagleg\\Desktop\\ML DL\\ISOLAB-project\\config\\isolab-agri-support-firebase-adminsdk-fbsvc-73184d48a6.json"
        
        if not os.path.exists(service_key_path):
            print(f"Warning: Firebase service account key not found at {service_key_path}")
            print("Some features may not work. Please check FIREBASE_SETUP.md for configuration instructions.")
            return False
        
        # Initialize Firebase
        cred = credentials.Certificate(service_key_path)
        firebase_app = firebase_admin.initialize_app(cred)
        
        # Initialize Firestore DB
        db = firestore.client()
        
        print("Firebase initialized successfully")
        return True
        
    except Exception as e:
        print(f"Firebase initialization failed: {e}")
        return False

def get_db():
    """Get Firestore database instance"""
    return db

def is_firebase_available():
    """Check if Firebase is properly initialized"""
    return db is not None
