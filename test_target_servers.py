#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

def test_target_servers():
    # Login and get session
    session = requests.Session()
    login_data = {"username": "apigee_admin", "password": "ApigeeAdmin2024!"}
    session.post("http://localhost:5001/login", data=login_data)

    # Set token
    token_data = {"gcp_token": TOKEN}
    session.post("http://localhost:5001/auth", data=token_data)

    # Get organizations
    orgs_response = session.get("http://localhost:5001/api/organizations")
    orgs = orgs_response.json()["organizations"]
    print(f"Available orgs: {orgs[:2]}")

    # Get environments for first org
    org = orgs[0]
    env_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments")
    envs = env_response.json()
    print(f"Environments response: {json.dumps(envs, indent=2)[:300]}")

    if "environments" in envs and envs["environments"]:
        env_name = envs["environments"][0]["name"]
        print(f"Testing with org: {org}, env: {env_name}")
        
        # Test target servers
        ts_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments/{env_name}/targetservers")
        print(f"Target Servers Response Status: {ts_response.status_code}")
        print(f"Target Servers Response: {json.dumps(ts_response.json(), indent=2)}")

if __name__ == "__main__":
    test_target_servers()
