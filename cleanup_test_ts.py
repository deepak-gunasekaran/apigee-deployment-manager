#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

org = "irx-apm1082662-gld-01c5"
environments = ["digiapi-preprod-1", "digiapi-preprod-2"]

# Clean up test target servers
test_data = {
    "name": "test-multi-ts-8221",
    "environments": environments
}

print("Cleaning up test target servers...")
response = session.delete(f"http://localhost:5001/api/organizations/{org}/targetservers/multi", 
                         json=test_data)

print(f"Cleanup response: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Cleanup results: {json.dumps(result, indent=2)}")
else:
    print(f"Cleanup error: {response.text}")
