#!/usr/bin/env python3
"""
Simple test to verify login functionality
"""

import requests
import json

def test_login():
    """Test login with different credentials"""
    
    base_url = "http://127.0.0.1:5000"
    
    # Test cases
    test_cases = [
        {
            "name": "Admin by username",
            "data": {"username": "admin", "password": "admin123"}
        },
        {
            "name": "Admin by email", 
            "data": {"email": "admin@isolab.com", "password": "admin123"}
        },
        {
            "name": "Technician 1",
            "data": {"username": "technicien1", "password": "tech123"}
        },
        {
            "name": "Invalid password",
            "data": {"username": "admin", "password": "wrong"}
        },
        {
            "name": "Invalid user",
            "data": {"username": "nonexistent", "password": "test"}
        }
    ]
    
    print("🔍 Testing Login Functionality")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Data: {test_case['data']}")
        
        try:
            response = requests.post(
                f"{base_url}/login",
                headers={"Content-Type": "application/json"},
                json=test_case['data'],
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            try:
                result = response.json()
                if response.status_code == 200:
                    user = result.get('user', {})
                    print(f"   ✅ Success: {user.get('username')} ({user.get('role')})")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            except:
                print(f"   ❌ Invalid JSON response")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {e}")
    
    print(f"\n{'='*50}")
    print("🎯 Login test completed!")

if __name__ == "__main__":
    test_login()
