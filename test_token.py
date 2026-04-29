#!/usr/bin/env python3
"""
Test script to verify GCP token and Apigee API response parsing
"""
import requests
import json

# Your GCP token
TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

def test_direct_api():
    """Test direct Apigee API call"""
    print("=== Testing Direct Apigee API ===")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get("https://apigee.googleapis.com/v1/organizations", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Raw Response: {json.dumps(data, indent=2)}")
            
            # Extract organization names
            organizations = []
            if 'organizations' in data:
                for org in data['organizations']:
                    if isinstance(org, dict) and 'organization' in org:
                        organizations.append(org['organization'])
            
            print(f"Extracted Organizations: {organizations}")
            return organizations
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []

def test_webapp_api():
    """Test webapp API endpoint"""
    print("\n=== Testing Webapp API ===")
    
    # First login
    session = requests.Session()
    login_data = {
        'username': 'apigee_admin',
        'password': 'ApigeeAdmin2024!'
    }
    
    try:
        # Login
        login_response = session.post('http://localhost:5001/login', data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200 or login_response.status_code == 302:
            # Set GCP token
            token_data = {'gcp_token': TOKEN}
            auth_response = session.post('http://localhost:5001/auth', data=token_data)
            print(f"Auth Status: {auth_response.status_code}")
            
            # Test organizations endpoint
            org_response = session.get('http://localhost:5001/api/organizations')
            print(f"Organizations API Status: {org_response.status_code}")
            
            if org_response.status_code == 200:
                data = org_response.json()
                print(f"Webapp Response: {json.dumps(data, indent=2)}")
                return data.get('organizations', [])
            else:
                print(f"Organizations API Error: {org_response.text}")
                return []
        else:
            print(f"Login failed: {login_response.text}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []

if __name__ == "__main__":
    print("Testing GCP Token and API Response Parsing")
    print("=" * 50)
    
    # Test direct API
    direct_orgs = test_direct_api()
    
    # Test webapp API
    webapp_orgs = test_webapp_api()
    
    print("\n=== Summary ===")
    print(f"Direct API Organizations: {direct_orgs}")
    print(f"Webapp API Organizations: {webapp_orgs}")
    
    if direct_orgs == webapp_orgs and len(direct_orgs) > 0:
        print("✅ SUCCESS: Both APIs return the same organizations")
    else:
        print("❌ MISMATCH: APIs return different results")
