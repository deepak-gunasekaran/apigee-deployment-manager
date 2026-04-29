#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

# Test direct API calls to understand KVM structure
headers = {"Authorization": f"Bearer {TOKEN}"}

# Try different orgs that might have KVMs
orgs_to_test = [
    "irx-apm1082662-gld-01c5",
    "irx-apm1081130-gld-0196", 
    "irx-apm1082662-slvr-013l"
]

for org in orgs_to_test:
    print(f"\n=== Testing org: {org} ===")
    
    # Get environments
    env_response = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/environments", headers=headers)
    if env_response.status_code != 200:
        print(f"Can't access environments: {env_response.status_code}")
        continue
        
    environments = env_response.json()
    env_list = environments if isinstance(environments, list) else environments.get('environments', [])
    
    if not env_list:
        print("No environments found")
        continue
        
    # Test first environment
    env = env_list[0] if isinstance(env_list[0], str) else env_list[0].get('name')
    print(f"Testing environment: {env}")
    
    # Get KVMs
    kvm_response = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/environments/{env}/keyvaluemaps", headers=headers)
    print(f"KVMs response: {kvm_response.status_code}")
    
    if kvm_response.status_code == 200:
        kvms = kvm_response.json()
        print(f"KVMs found: {kvms}")
        
        if isinstance(kvms, list) and len(kvms) > 0:
            # Test first KVM
            kvm_name = kvms[0] if isinstance(kvms[0], str) else kvms[0].get('name')
            print(f"\nTesting KVM entries for: {kvm_name}")
            
            entries_response = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/environments/{env}/keyvaluemaps/{kvm_name}/entries", headers=headers)
            print(f"KVM entries response: {entries_response.status_code}")
            
            if entries_response.status_code == 200:
                entries = entries_response.json()
                print(f"KVM entries structure: {json.dumps(entries, indent=2)}")
            else:
                print(f"KVM entries error: {entries_response.text}")
                
            break  # Found working org/env/kvm
    else:
        print(f"KVMs error: {kvm_response.text}")
