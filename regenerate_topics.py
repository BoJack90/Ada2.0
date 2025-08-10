#!/usr/bin/env python3
"""Regenerate topics for content plan using API"""
import requests
import json

# API configuration
API_URL = "http://localhost:8090"
EMAIL = "essa@essa.pl"
PASSWORD = "Dragi2!!"  # Default password from earlier in conversation

# Login first
login_data = {
    "username": EMAIL,
    "password": PASSWORD
}

response = requests.post(f"{API_URL}/api/v1/auth/login", data=login_data)
if response.status_code != 200:
    print(f"Login failed: {response.text}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Trigger topic generation
response = requests.post(f"{API_URL}/api/v1/content-plans/6/generate", headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))