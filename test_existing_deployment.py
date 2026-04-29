#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

org = "irx-apm1082662-gld-01c5"
env = "digiapi-preprod-1"

print("Testing existing deployment functionality...")

# Test existing API proxy deployment (no file upload)
existing_deployment_data = {
    "deployment_type": "api_proxy",
    "organization": org,
    "environment": env,
    "existing_proxy": "healthcheck",  # Using a common proxy name
    "revision": "1"
}

print(f"\nTesting existing API proxy deployment:")
print(f"Data: {json.dumps(existing_deployment_data, indent=2)}")

response = session.post("http://localhost:5001/deploy", data=existing_deployment_data)
print(f"Status: {response.status_code}")
print(f"Response length: {len(response.text)}")

# Check if response contains success or error messages
if "deployed successfully" in response.text:
    print("✅ SUCCESS: Deployment successful message found")
elif "error" in response.text.lower():
    print("❌ ERROR: Error message found in response")
    # Extract error message if possible
    if "flash" in response.text or "alert" in response.text:
        print("Response contains flash/alert messages")
else:
    print("ℹ️  Response doesn't contain clear success/error indicators")

# Check for any file upload related errors
if "upload" in response.text.lower() or "zip" in response.text.lower():
    print("⚠️  WARNING: Response mentions upload/zip - might be asking for file")
else:
    print("✅ No file upload requirements detected")

print(f"\nFirst 500 chars of response:")
print(response.text[:500])
