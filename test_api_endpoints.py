#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

org = "irx-apm1082662-gld-01c5"
env = "digiapi-preprod-1"

print("Testing API endpoints...")

# Test API proxies endpoint
print(f"\n1. Testing API Proxies endpoint:")
print(f"URL: /api/organizations/{org}/apis")
response = session.get(f"http://localhost:5001/api/organizations/{org}/apis")
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Response: {response.text[:500]}...")

# Test shared flows endpoint (all)
print(f"\n2. Testing Shared Flows endpoint (all):")
print(f"URL: /api/organizations/{org}/sharedflows")
response = session.get(f"http://localhost:5001/api/organizations/{org}/sharedflows")
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Response: {response.text[:500]}...")

# Test deployed shared flows endpoint
print(f"\n3. Testing Deployed Shared Flows endpoint:")
print(f"URL: /api/organizations/{org}/environments/{env}/sharedflows/deployments")
response = session.get(f"http://localhost:5001/api/organizations/{org}/environments/{env}/sharedflows/deployments")
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Response: {response.text[:500]}...")

# Test direct Apigee API calls
print(f"\n4. Testing direct Apigee API calls:")
headers = {"Authorization": f"Bearer {TOKEN}"}

print(f"\nDirect API Proxies call:")
response = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/apis", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"API Proxies count: {len(data) if isinstance(data, list) else 'Not a list'}")
    if isinstance(data, list) and len(data) > 0:
        print(f"First few proxies: {data[:3]}")
else:
    print(f"Error: {response.text[:200]}")

print(f"\nDirect Shared Flows call:")
response = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/sharedflows", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Response structure: {type(data)}")
    if isinstance(data, dict):
        print(f"Keys: {list(data.keys())}")
        if 'sharedFlows' in data:
            print(f"Shared flows count: {len(data['sharedFlows'])}")
else:
    print(f"Error: {response.text[:200]}")

print(f"\nDirect Deployed Shared Flows call:")
response = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/environments/{env}/sharedflows", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Response structure: {type(data)}")
    print(f"Response: {json.dumps(data, indent=2)[:500]}...")
else:
    print(f"Error: {response.text[:200]}")
