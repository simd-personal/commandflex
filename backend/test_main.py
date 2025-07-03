#!/usr/bin/env python3
"""
Simple test script to verify CommandFlex backend functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_auth():
    """Test authentication endpoints"""
    try:
        # Test login
        login_data = {
            "username": "dispatcher",
            "password": "password123"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("✅ Login successful")
            
            # Test protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ User authenticated: {user_data.get('full_name')}")
                return True
            else:
                print(f"❌ User auth failed: {response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth test error: {e}")
        return False

def test_incidents():
    """Test incidents endpoints"""
    try:
        # Get auth token first
        login_data = {"username": "dispatcher", "password": "password123"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test get incidents
        response = requests.get(f"{BASE_URL}/api/incidents", headers=headers)
        if response.status_code == 200:
            incidents = response.json()
            print(f"✅ Retrieved {len(incidents.get('incidents', []))} incidents")
            return True
        else:
            print(f"❌ Get incidents failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Incidents test error: {e}")
        return False

def test_units():
    """Test units endpoints"""
    try:
        # Get auth token first
        login_data = {"username": "dispatcher", "password": "password123"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test get units
        response = requests.get(f"{BASE_URL}/api/units", headers=headers)
        if response.status_code == 200:
            units = response.json()
            print(f"✅ Retrieved {len(units.get('units', []))} units")
            return True
        else:
            print(f"❌ Get units failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Units test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚨 CommandFlex Backend Test Suite")
    print("==================================")
    print()
    
    tests = [
        ("Health Check", test_health),
        ("Authentication", test_auth),
        ("Incidents API", test_incidents),
        ("Units API", test_units),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
        time.sleep(1)  # Small delay between tests
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 