#!/usr/bin/env python3
"""Test content visualization API endpoints"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

# Test credentials
BASE_URL = "http://localhost:8090"
EMAIL = "test@example.com"
PASSWORD = "securepassword123"

# Login first
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    data={"username": EMAIL, "password": PASSWORD}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get organization ID
orgs_response = requests.get(
    f"{BASE_URL}/api/v1/organizations",
    headers=headers
)
organization_id = orgs_response.json()[0]["id"]

print(f"=== TESTING CONTENT PLANS SUMMARY API ===")
print(f"Organization ID: {organization_id}\n")

# Test content plans summary endpoint
summary_response = requests.get(
    f"{BASE_URL}/api/content-plans/summary",
    params={"organization_id": organization_id},
    headers=headers
)

if summary_response.status_code == 200:
    plans = summary_response.json()
    print(f"Found {len(plans)} content plans\n")
    
    for plan in plans[:2]:  # Show first 2 plans
        print(f"Plan: {plan['plan_period']}")
        print(f"  Status: {plan['status']}")
        print(f"  Blog quota: {plan['blog_posts_quota']}")
        print(f"  SM quota: {plan['sm_posts_quota']}")
        print(f"  Stats: {json.dumps(plan['content_stats'], indent=4)}")
        print()
        
        # Test visualization endpoint for this plan
        if plan['id']:
            print(f"=== TESTING VISUALIZATION FOR PLAN {plan['id']} ===")
            viz_response = requests.get(
                f"{BASE_URL}/api/content-plans/{plan['id']}/visualization",
                headers=headers
            )
            
            if viz_response.status_code == 200:
                viz_data = viz_response.json()
                print(f"Blog posts: {len(viz_data['blogPosts'])}")
                print(f"Social posts: {len(viz_data['socialPosts'])}")
                
                # Show sample blog post
                if viz_data['blogPosts']:
                    blog = viz_data['blogPosts'][0]
                    print(f"\nSample blog post:")
                    print(f"  Title: {blog['title']}")
                    print(f"  Variants: {len(blog['variants'])}")
                    if blog['variants']:
                        print(f"  Content preview: {blog['variants'][0]['content_text'][:100]}...")
                
                # Show sample social post
                if viz_data['socialPosts']:
                    social = viz_data['socialPosts'][0]
                    print(f"\nSample social post:")
                    print(f"  Title: {social['title']}")
                    print(f"  Platform: {social['platform']}")
                    print(f"  Source: {social['source_type']}")
                    print(f"  Parent ID: {social['parent_id']}")
                    if social['variants']:
                        print(f"  Content: {social['variants'][0]['content_text'][:100]}...")
            else:
                print(f"Visualization API error: {viz_response.status_code}")
                print(viz_response.text)
            
            print("\n" + "="*50 + "\n")
            break  # Only test one plan in detail
else:
    print(f"Summary API error: {summary_response.status_code}")
    print(summary_response.text)