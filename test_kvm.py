#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

# Try irx-apm1082662-gld-01c5 org
org = "irx-apm1082662-gld-01c5"

envs_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments")
envs = envs_response.json()
env = envs[0] if isinstance(envs, list) else envs["environments"][0]["name"]

print(f"Testing KVMs for org: {org}, env: {env}")

# Get KVMs list
kvms_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments/{env}/keyvaluemaps")
print(f"KVMs response: {kvms_response.status_code}")
kvms_data = kvms_response.json()
print(f"KVMs data: {json.dumps(kvms_data, indent=2)}")

# Test getting entries for first KVM if available
if isinstance(kvms_data, list) and len(kvms_data) > 0:
    kvm_name = kvms_data[0] if isinstance(kvms_data[0], str) else kvms_data[0].get('name', kvms_data[0])
    print(f"\nTesting KVM entries for: {kvm_name}")
    
    # Test direct API call to get KVM entries
    headers = {"Authorization": f"Bearer {TOKEN}"}
    entries_response = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/environments/{env}/keyvaluemaps/{kvm_name}/entries", headers=headers)
    print(f"KVM entries response: {entries_response.status_code}")
    if entries_response.status_code == 200:
        print(f"KVM entries: {json.dumps(entries_response.json(), indent=2)}")
    else:
        print(f"KVM entries error: {entries_response.text}")
