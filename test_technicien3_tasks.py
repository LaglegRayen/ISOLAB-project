#!/usr/bin/env python3
"""
Quick test to check if technicien3's tasks are working
"""

import requests
import json

def test_technicien3_tasks():
    """Test if technicien3 can see their tasks now"""
    
    print("🧪 Testing technicien3 tasks after fix...")
    
    # Login as technicien3
    session = requests.Session()
    login_response = session.post('http://127.0.0.1:5000/login', json={
        'username': 'technicien3',
        'password': 'tech123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Test my-tasks endpoint
    print("\n🔍 Testing /stages/my-tasks...")
    tasks_response = session.get('http://127.0.0.1:5000/stages/my-tasks')
    
    if tasks_response.status_code == 200:
        tasks_data = tasks_response.json()
        tasks = tasks_data.get('tasks', [])
        print(f"📋 Found {len(tasks)} tasks")
        
        if tasks:
            print("Tasks:")
            for i, task in enumerate(tasks[:5], 1):  # Show first 5
                machine_info = task.get('machine_info', {})
                print(f"  {i}. {task.get('stage_label')} - Machine: {machine_info.get('serialNumber')} - Status: {task.get('status')}")
        else:
            print("⚠️  No tasks found")
    else:
        print(f"❌ Tasks API failed: {tasks_response.status_code}")
        print(f"Response: {tasks_response.text}")
    
    # Test dashboard endpoint
    print("\n📊 Testing /stages/dashboard...")
    dashboard_response = session.get('http://127.0.0.1:5000/stages/dashboard')
    
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        print(f"Dashboard stats:")
        print(f"  Pending tasks: {dashboard_data.get('my_pending_tasks')}")
        print(f"  Completed tasks: {dashboard_data.get('my_completed_tasks')}")
        print(f"  Machines in my stages: {dashboard_data.get('machines_in_my_stages')}")
        print(f"  Total machines: {dashboard_data.get('total_machines')}")
    else:
        print(f"❌ Dashboard API failed: {dashboard_response.status_code}")
        print(f"Response: {dashboard_response.text}")

if __name__ == "__main__":
    test_technicien3_tasks()
