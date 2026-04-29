#!/usr/bin/env python3
import requests
import json

TOKEN = "YOUR_GCP_OAUTH_TOKEN_HERE"

session = requests.Session()
session.post("http://localhost:5001/login", data={"username": "apigee_admin", "password": "ApigeeAdmin2024!"})
session.post("http://localhost:5001/auth", data={"gcp_token": TOKEN})

orgs = session.get("http://localhost:5001/api/organizations").json()["organizations"]
org = orgs[0]
print(f"Using org: {org}")

envs_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments")
print(f"Environments response: {json.dumps(envs_response.json(), indent=2)}")

envs_data = envs_response.json()
if isinstance(envs_data, list):
    env = envs_data[0]
elif isinstance(envs_data, dict) and "environments" in envs_data:
    env = envs_data["environments"][0]["name"]
else:
    env = "test"  # fallback

print(f"Using env: {env}")

ts_response = session.get(f"http://localhost:5001/api/organizations/{org}/environments/{env}/targetservers")
print(f"Target servers response: {ts_response.status_code}")
print(f"Target servers data: {json.dumps(ts_response.json(), indent=2)}")
