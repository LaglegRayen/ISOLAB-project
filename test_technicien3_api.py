#!/usr/bin/env python3
"""
Test the actual API endpoints that technicien3 would use in the web app
"""

import requests
import json

def test_technicien3_api_access():
    """Test API access for technicien3"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing technicien3 API Access")
    print("=" * 50)
    
    # Step 1: Login as technicien3
    print("1. Logging in as technicien3...")
    
    login_data = {
        "username": "technicien3",
        "password": "tech123"
    }
    
    session = requests.Session()
    
    try:
        login_response = session.post(
            f"{base_url}/login",
            headers={"Content-Type": "application/json"},
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            user = login_result.get('user', {})
            print(f"   ✅ Login successful: {user.get('username')} ({user.get('role')})")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Step 2: Test machines API
    print(f"\n2. Testing /machines API...")
    
    try:
        machines_response = session.get(f"{base_url}/machines", timeout=10)
        
        if machines_response.status_code == 200:
            machines_data = machines_response.json()
            machines = machines_data.get('machines', [])
            print(f"   ✅ Machines API successful")
            print(f"   Machines returned: {len(machines)}")
            
            if machines:
                print(f"   Sample machine:")
                sample = machines[0]
                print(f"     - ID: {sample.get('id')}")
                print(f"     - Name: {sample.get('nom_machine', 'Unknown')}")
                print(f"     - Current Stage: {sample.get('current_stage', 'Unknown')}")
                print(f"     - Workflow Status: {sample.get('workflow_status', 'Unknown')}")
            else:
                print(f"   ⚠️  No machines returned - this might be the issue!")
        else:
            print(f"   ❌ Machines API failed: {machines_response.status_code}")
            print(f"   Error: {machines_response.text}")
            
    except Exception as e:
        print(f"   ❌ Machines API error: {e}")
    
    # Step 3: Test workflows API  
    print(f"\n3. Testing /workflows API...")
    
    try:
        workflows_response = session.get(f"{base_url}/workflows", timeout=10)
        
        if workflows_response.status_code == 200:
            workflows_data = workflows_response.json()
            workflows = workflows_data.get('workflows', [])
            print(f"   ✅ Workflows API successful")
            print(f"   Workflows returned: {len(workflows)}")
            
            if workflows:
                print(f"   Sample workflow:")
                sample = workflows[0]
                print(f"     - Machine ID: {sample.get('machine_id')}")
                print(f"     - Status: {sample.get('status', 'Unknown')}")
                stages = sample.get('stages', [])
                print(f"     - Stages: {len(stages)}")
                for stage in stages[:2]:  # Show first 2 stages
                    print(f"       * {stage.get('label')} - {stage.get('status')}")
            else:
                print(f"   ⚠️  No workflows returned!")
        else:
            print(f"   ❌ Workflows API failed: {workflows_response.status_code}")
            print(f"   Error: {workflows_response.text}")
            
    except Exception as e:
        print(f"   ❌ Workflows API error: {e}")
    
    print(f"\n" + "=" * 50)
    print("🎯 Test completed!")

def main():
    test_technicien3_api_access()

if __name__ == "__main__":
    main()
