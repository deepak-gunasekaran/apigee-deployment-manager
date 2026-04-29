#!/usr/bin/env python3
import requests
import json
import time

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

org = "irx-apm1082662-gld-01c5"

# Get environments first
envs_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments")
print(f"Environments response: {envs_response.status_code}")
if envs_response.status_code == 200:
    envs_data = envs_response.json()
    environments = envs_data if isinstance(envs_data, list) else envs_data.get('environments', [])
    env_names = [env if isinstance(env, str) else env.get('name') for env in environments]
    print(f"Available environments: {env_names[:5]}")  # Show first 5
    
    # Test multi-environment target server creation
    test_data = {
        "name": "test-multi-ts-" + str(int(time.time()) % 10000),
        "host": "test.example.com",
        "port": 443,
        "isEnabled": True,
        "protocol": "HTTP",
        "environments": env_names[:2]  # Test with first 2 environments
    }
    
    print(f"\nTesting multi-environment target server creation...")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    response = session.post(f"http://localhost:5001/api/organizations/{org}/targetservers/multi", 
                           json=test_data)
    
    print(f"\nMulti-env response: {response.status_code}")
    print(f"Response data: {json.dumps(response.json(), indent=2)}")
    
else:
    print(f"Failed to get environments: {envs_response.text}")

# Also test direct Apigee API to see what format it expects
print(f"\n=== Testing Direct Apigee API ===")
headers = {"Authorization": f"Bearer {TOKEN}"}

# Try creating a target server directly via Apigee API
direct_data = {
    "name": "test-direct-ts",
    "host": "test.example.com", 
    "port": 443,
    "isEnabled": True,
    "protocol": "HTTP"
}

env_to_test = env_names[0] if 'env_names' in locals() else "digiapi-preprod-1"
direct_response = requests.post(
    f"https://apigee.googleapis.com/v1/organizations/{org}/environments/{env_to_test}/targetservers",
    headers=headers,
    json=direct_data
)

print(f"Direct API response: {direct_response.status_code}")
if direct_response.status_code != 200:
    print(f"Direct API error: {direct_response.text}")
else:
    print("Direct API success!")
    # Clean up - delete the test target server
    delete_response = requests.delete(
        f"https://apigee.googleapis.com/v1/organizations/{org}/environments/{env_to_test}/targetservers/test-direct-ts",
        headers=headers
    )
    print(f"Cleanup response: {delete_response.status_code}")
