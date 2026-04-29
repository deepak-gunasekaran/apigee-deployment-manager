#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

org = "irx-apm1082662-gld-01c5"
env = "digiapi-preprod-1"
kvm_name = "Anthem_digital_products_Kvm"

print(f"Testing webapp KVM entries API...")
print(f"Org: {org}, Env: {env}, KVM: {kvm_name}")

# Test KVMs list first
kvms_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments/{env}/keyvaluemaps")
print(f"\nKVMs list response: {kvms_response.status_code}")
if kvms_response.status_code == 200:
    kvms_data = kvms_response.json()
    print(f"KVMs found: {len(kvms_data) if isinstance(kvms_data, list) else 'Not a list'}")
    if isinstance(kvms_data, list) and len(kvms_data) > 0:
        print(f"First few KVMs: {kvms_data[:3]}")
else:
    print(f"KVMs error: {kvms_response.text}")

# Test KVM entries
entries_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments/{env}/keyvaluemaps/{kvm_name}/entries")
print(f"\nKVM entries response: {entries_response.status_code}")
if entries_response.status_code == 200:
    entries_data = entries_response.json()
    print(f"KVM entries data: {json.dumps(entries_data, indent=2)}")
else:
    print(f"KVM entries error: {entries_response.text}")
