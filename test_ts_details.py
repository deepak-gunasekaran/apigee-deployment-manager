#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

# Test direct API call to get target server details
headers = {"Authorization": f"Bearer {TOKEN}"}
org = "irx-apm1081130-gld-0196"
env = "digiapi-preprod-1"
ts_name = "agadia-server"

print(f"Testing target server details for: {ts_name}")
response = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/environments/{env}/targetservers/{ts_name}", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
