#!/usr/bin/env python3
"""
Debug the exact machine filtering issue for technicien3
"""

import requests
import json

def debug_technicien3_machines():
    """Debug why technicien3 can't see machines"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🐛 Debugging technicien3 machines access")
    print("=" * 60)
    
    # Login as technicien3
    session = requests.Session()
    
    login_data = {"username": "technicien3", "password": "tech123"}
    login_response = session.post(f"{base_url}/login", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    print("✅ Login successful")
    
    # Test the exact endpoint the frontend calls
    print(f"\n🔍 Testing GET /machines endpoint...")
    
    machines_response = session.get(f"{base_url}/machines", timeout=10)
    
    print(f"Response Status: {machines_response.status_code}")
    print(f"Response Headers: {dict(machines_response.headers)}")
    
    try:
        response_data = machines_response.json()
        
        print(f"\n📄 Response Data Structure:")
        print(f"Keys: {list(response_data.keys())}")
        
        if 'data' in response_data:
            machines = response_data['data']
            print(f"Machines count: {len(machines)}")
            
            if len(machines) == 0:
                print(f"⚠️  No machines returned!")
                
                # Let's check what the session contains
                print(f"\n🔍 Checking session data...")
                current_user_response = session.get(f"{base_url}/users/current", timeout=10)
                if current_user_response.status_code == 200:
                    user_data = current_user_response.json()
                    print(f"Current user: {json.dumps(user_data, indent=2)}")
                    
        elif 'error' in response_data:
            print(f"❌ API Error: {response_data['error']}")
        
        print(f"\nFull Response:")
        print(json.dumps(response_data, indent=2))
        
    except Exception as e:
        print(f"❌ Error parsing response: {e}")
        print(f"Raw response: {machines_response.text}")
    
    # Let's also check if there are any session issues by testing admin
    print(f"\n" + "="*60)
    print(f"🔍 Testing with admin for comparison...")
    
    admin_session = requests.Session()
    admin_login = {"username": "admin", "password": "admin123"}
    admin_login_response = admin_session.post(f"{base_url}/login", json=admin_login, timeout=10)
    
    if admin_login_response.status_code == 200:
        admin_machines_response = admin_session.get(f"{base_url}/machines", timeout=10)
        if admin_machines_response.status_code == 200:
            admin_data = admin_machines_response.json()
            admin_machines = admin_data.get('data', [])
            print(f"Admin sees {len(admin_machines)} machines")
        else:
            print(f"Admin API failed: {admin_machines_response.status_code}")
    else:
        print(f"Admin login failed: {admin_login_response.status_code}")

def main():
    debug_technicien3_machines()

if __name__ == "__main__":
    main()
