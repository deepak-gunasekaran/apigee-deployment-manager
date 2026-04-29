#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

org = "irx-apm1082662-gld-01c5"

# Get environments
envs_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments")
if envs_response.status_code == 200:
    envs_data = envs_response.json()
    environments = envs_data if isinstance(envs_data, list) else envs_data.get('environments', [])
    env_names = [env if isinstance(env, str) else env.get('name') for env in environments]
    print(f"Available environments: {env_names}")
    
    # Test with a target server name that might already exist
    test_data = {
        "name": "test-existing-server",  # Use a name that might already exist
        "host": "updated.example.com",
        "port": 443,
        "isEnabled": True,
        "protocol": "HTTP",
        "environments": env_names[:4]  # Test with first 4 environments
    }
    
    print(f"\nTesting multi-environment creation with potentially existing server...")
    print(f"Testing environments: {test_data['environments']}")
    
    response = session.post(f"http://localhost:5001/api/organizations/{org}/targetservers/multi", 
                           json=test_data)
    
    print(f"\nMulti-env response: {response.status_code}")
    result = response.json()
    print(f"Response data: {json.dumps(result, indent=2)}")
    
    # Check for 409 errors specifically
    if result.get('errors'):
        for error in result['errors']:
            if '409' in error.get('error', ''):
                print(f"\n409 Conflict found in environment: {error['environment']}")
                print(f"Details: {error.get('details', 'No details')}")

# Also test direct API to see what 409 looks like
print(f"\n=== Testing Direct API for 409 ===")
headers = {"Authorization": f"Bearer {TOKEN}"}

# Try creating a target server that might already exist
direct_data = {
    "name": "test-existing-server",
    "host": "direct.example.com", 
    "port": 443,
    "isEnabled": True,
    "protocol": "HTTP"
}

if 'env_names' in locals():
    env_to_test = env_names[0]
    direct_response = requests.post(
        f"https://apigee.googleapis.com/v1/organizations/{org}/environments/{env_to_test}/targetservers",
        headers=headers,
        json=direct_data
    )
    
    print(f"Direct API response: {direct_response.status_code}")
    if direct_response.status_code == 409:
        print(f"409 Conflict details: {direct_response.text}")
    elif direct_response.status_code != 200:
        print(f"Other error: {direct_response.text}")
    else:
        print("Direct API success - server created")
        # Clean up
        delete_response = requests.delete(
            f"https://apigee.googleapis.com/v1/organizations/{org}/environments/{env_to_test}/targetservers/test-existing-server",
            headers=headers
        )
        print(f"Cleanup response: {delete_response.status_code}")
