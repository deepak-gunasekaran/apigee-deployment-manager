#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

org = "irx-apm1082662-gld-01c5"
env = "digiapi-preprod-1"

# Test single-environment KVM creation
test_kvm_data = {
    "name": "test-single-kvm",
    "encrypted": False
}

print(f"Testing single-environment KVM creation...")
print(f"Org: {org}, Env: {env}")
print(f"Data: {json.dumps(test_kvm_data, indent=2)}")

response = session.post(f"http://localhost:5001/api/organizations/{org}/environments/{env}/keyvaluemaps", 
                       json=test_kvm_data)

print(f"\nKVM creation response: {response.status_code}")
print(f"Response headers: {dict(response.headers)}")
print(f"Response content: {response.text}")

if response.status_code == 200:
    try:
        result = response.json()
        print(f"JSON response: {json.dumps(result, indent=2)}")
    except:
        print("Response is not valid JSON")
else:
    print(f"Error response: {response.text}")

# Clean up - delete the test KVM
if response.status_code == 200:
    print(f"\nCleaning up test KVM...")
    delete_response = session.delete(f"http://localhost:5001/api/organizations/{org}/environments/{env}/keyvaluemaps/test-single-kvm")
    print(f"Cleanup response: {delete_response.status_code}")
    if delete_response.status_code == 200:
        print("Test KVM cleaned up successfully")
    else:
        print(f"Cleanup error: {delete_response.text}")
