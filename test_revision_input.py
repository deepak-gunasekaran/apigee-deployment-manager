#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

org = "irx-apm1082662-gld-01c5"
env = "digiapi-preprod-1"

print("Testing revision input issue for both API Proxy and Shared Flow...")

# Test 1: API Proxy with manually typed revision number
print("\n=== Test 1: API Proxy with manually typed revision 5 ===")
api_deployment_data = {
    "deployment_type": "api_proxy",
    "organization": org,
    "environment": env,
    "existing_proxy": "healthcheck",
    "revision": "5",  # Manually typed revision number
    "existing_deployment_option": "redeploy"  # Ensure we're redeploying existing
}

print(f"Sending data: {json.dumps(api_deployment_data, indent=2)}")

response = session.post("http://localhost:5001/deploy", data=api_deployment_data)
print(f"Status: {response.status_code}")

# Check if the response contains the revision number we sent
if "revision 5" in response.text:
    print("✅ SUCCESS: API Proxy revision 5 was used correctly")
elif "revision 1" in response.text:
    print("❌ ISSUE: API Proxy revision defaulted to 1 instead of using 5")
elif "deployed successfully" in response.text:
    print("⚠️  PARTIAL: API Proxy deployed but revision number unclear in response")
else:
    print("ℹ️  API Proxy response doesn't contain clear revision information")

# Test 2: Shared Flow with manually typed revision number
print("\n=== Test 2: Shared Flow with manually typed revision 3 ===")
sf_deployment_data = {
    "deployment_type": "shared_flow",
    "organization": org,
    "environment": env,
    "existing_sharedflow": "AddJwt-Digiapi-Shared-CORE-V1",
    "sf_revision": "3",  # Manually typed revision number
    "existing_sf_deployment_option": "redeploy"  # Ensure we're redeploying existing
}

print(f"Sending data: {json.dumps(sf_deployment_data, indent=2)}")

response = session.post("http://localhost:5001/deploy", data=sf_deployment_data)
print(f"Status: {response.status_code}")

# Check if the response contains the revision number we sent
if "revision 3" in response.text:
    print("✅ SUCCESS: Shared Flow revision 3 was used correctly")
elif "revision 1" in response.text:
    print("❌ ISSUE: Shared Flow revision defaulted to 1 instead of using 3")
elif "deployed successfully" in response.text:
    print("⚠️  PARTIAL: Shared Flow deployed but revision number unclear in response")
else:
    print("ℹ️  Shared Flow response doesn't contain clear revision information")

# Test 3: Edge case - Very high revision number
print("\n=== Test 3: API Proxy with high revision number 99 ===")
high_revision_data = {
    "deployment_type": "api_proxy",
    "organization": org,
    "environment": env,
    "existing_proxy": "healthcheck",
    "revision": "99",  # High revision number
    "existing_deployment_option": "redeploy"
}

print(f"Sending data: {json.dumps(high_revision_data, indent=2)}")

response = session.post("http://localhost:5001/deploy", data=high_revision_data)
print(f"Status: {response.status_code}")

if "revision 99" in response.text:
    print("✅ SUCCESS: High revision number 99 was used correctly")
elif "revision 1" in response.text:
    print("❌ ISSUE: High revision defaulted to 1 instead of using 99")
elif "failed" in response.text.lower() or "error" in response.text.lower():
    print("⚠️  EXPECTED: High revision number likely doesn't exist (this is normal)")
else:
    print("ℹ️  High revision response unclear")

print("\n" + "="*60)
print("DEBUGGING INSTRUCTIONS:")
print("="*60)
print("1. Check Docker logs for debug output:")
print("   docker logs apigee-deployment-webapp --tail 30")
print("\n2. Look for these debug lines:")
print("   [DEBUG] Existing proxy deployment - proxy_name: ..., revision: ...")
print("   [DEBUG] Existing shared flow deployment - sharedflow_name: ..., revision: ...")
print("   [DEBUG] All form data: {...}")
print("\n3. In browser console, check for:")
print("   Form submission data:")
print("   revision: [your_typed_number]")
print("   sf_revision: [your_typed_number]")
print("\n4. Test manually in browser:")
print("   - Open Deploy page → Existing tab")
print("   - Select proxy/shared flow")
print("   - Ensure 'Redeploy existing revision' is selected")
print("   - Type revision number manually")
print("   - Open browser console (F12)")
print("   - Click Deploy and check console logs")
