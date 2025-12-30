#!/usr/bin/env python3
"""
Script to test the full Admin User Management Flow via Kong Gateway.

Scenario:
1. Login as Admin to get Admin Token.
2. Create a new user (via POST /admin/users).
3. Retrieve user details to verify creation.
4. Update user Core Info & Activate user (via PUT /admin/users/{id}).
5. Update user Profiles (Identity & Health) (via PUT /admin/users/{id}).
6. Delete the user (via DELETE /admin/users/{id}).
7. Verify user is deleted (expecting 404).

Usage:
    python3 user-service/scripts/test_admin_user_flow.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import random
import time

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
BASE_URL = f"{GATEWAY_URL}/api/v1/user-service"

# Admin Credentials (must match create_admin_user.py defaults or env vars)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    INFO = '\033[94m'
    BOLD = '\033[1m'

def make_request(url, method="GET", data=None, headers=None):
    """Helper to make HTTP requests using standard library to avoid external deps."""
    if headers is None: headers = {}
    
    # Allow self-signed certs for localhost/dev
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    encoded_data = json.dumps(data).encode('utf-8') if data else None
    if data: 
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            res_data = response.read().decode('utf-8')
            return response.status, json.loads(res_data) if res_data else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try: 
            return e.code, json.loads(body)
        except:
            return e.code, {"raw": body}
    except Exception as e:
        print(f"{Colors.FAIL}Connection Error to {url}: {e}{Colors.ENDC}")
        sys.exit(1)

def run_test():
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Testing Admin User Management Flow (via Kong Gateway){Colors.ENDC}")
    print(f"{Colors.INFO}Target: {BASE_URL}{Colors.ENDC}")
    
    # ---------------------------------------------------------
    # 0. Login as Admin
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[0] Logging in as Admin ({ADMIN_USERNAME})...{Colors.ENDC}")
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, 
        "password": ADMIN_PASSWORD
    })
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Admin Login failed. Please run 'create_admin_user.py' first.{Colors.ENDC}")
        print(json.dumps(admin_login, indent=2))
        sys.exit(1)

    admin_token = admin_login['data']['access_token']
    headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"{Colors.OKGREEN}✓ Admin logged in successfully.{Colors.ENDC}")

    # ---------------------------------------------------------
    # 1. Create New User
    # ---------------------------------------------------------
    rnd = random.randint(10000, 99999)
    # Ensure unique constraint on phone/email/username
    username = f"testuser_{rnd}"
    email = f"testuser_{rnd}@example.com"
    phone_num = f"09{rnd}12345" # Ensure unique phone number
    password = "UserPass123!"

    print(f"\n{Colors.BOLD}[1] Creating new user via Admin API...{Colors.ENDC}")
    print(f"    Payload: {username} | {email} | {phone_num}")
    
    create_payload = {
        "username": username,
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "Created",
        "phone_num": phone_num,
        "system_role": "user",
        "is_active": False # Explicitly creating as inactive first
    }

    status, create_res = make_request(f"{BASE_URL}/admin/users", "POST", create_payload, headers)

    if status != 201:
        print(f"{Colors.FAIL}❌ Create User failed: {create_res}{Colors.ENDC}")
        return

    user_data = create_res['data']
    user_id = user_data['user_id']
    print(f"{Colors.OKGREEN}✓ User created. ID: {user_id}{Colors.ENDC}")
    print(f"{Colors.INFO}    Role: {user_data.get('system_role')}, Active: {user_data.get('is_active')}{Colors.ENDC}")

    # ---------------------------------------------------------
    # 2. Get User Details
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[2] Retrieving user details...{Colors.ENDC}")
    status, get_res = make_request(f"{BASE_URL}/admin/users/{user_id}", "GET", headers=headers)

    if status != 200:
        print(f"{Colors.FAIL}❌ Get User failed: {get_res}{Colors.ENDC}")
        return
    
    fetched_user = get_res['data']
    if fetched_user['username'] == username and fetched_user['email'] == email:
        print(f"{Colors.OKGREEN}✓ User data verified.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Data mismatch!{Colors.ENDC}")

    # ---------------------------------------------------------
    # 3. Update Core Info & Activate User
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[3] Updating Core Info & Activating User...{Colors.ENDC}")
    update_core_payload = {
        "first_name": "UpdatedName",
        "is_active": True,
        "avatar_url": "http://example.com/avatar.png"
    }

    status, update_res = make_request(f"{BASE_URL}/admin/users/{user_id}", "PUT", update_core_payload, headers)

    if status != 200:
        print(f"{Colors.FAIL}❌ Update Core failed: {update_res}{Colors.ENDC}")
        return

    updated_data = update_res['data']
    if updated_data['is_active'] is True and updated_data['first_name'] == "UpdatedName":
        print(f"{Colors.OKGREEN}✓ User activated and name updated.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Update verification failed.{Colors.ENDC}")

    # ---------------------------------------------------------
    # 4. Update Nested Profiles (Identity & Health)
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[4] Updating Nested Profiles (Identity & Health)...{Colors.ENDC}")
    # Based on UserAdminUpdateSchema, we can nest these
    update_profile_payload = {
        "identity_profile": {
            "gender": "male",
            "date_of_birth": "1995-01-01",
            "occupation": "Engineer",
            "address": {
                "city": "Ho Chi Minh",
                "district": "District 1"
            }
        },
        "health_profile": {
            "height_cm": 175,
            "weight_kg": 70.5,
            "activity_level": "moderate",
            "health_goal": "maintain"
        }
    }

    status, profile_res = make_request(f"{BASE_URL}/admin/users/{user_id}", "PUT", update_profile_payload, headers)

    if status != 200:
        print(f"{Colors.FAIL}❌ Update Profiles failed: {profile_res}{Colors.ENDC}")
        return

    profile_data = profile_res['data']
    
    # Verify Identity
    ident = profile_data.get('identity_profile')
    if ident and ident.get('gender') == 'male' and ident.get('address', {}).get('city') == 'Ho Chi Minh':
        print(f"{Colors.OKGREEN}✓ Identity Profile updated.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Identity Profile mismatch: {ident}{Colors.ENDC}")

    # Verify Health
    health = profile_data.get('health_profile')
    if health and health.get('height_cm') == 175:
        print(f"{Colors.OKGREEN}✓ Health Profile updated.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Health Profile mismatch: {health}{Colors.ENDC}")

    # ---------------------------------------------------------
    # 5. Delete User
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[5] Deleting User...{Colors.ENDC}")
    status, del_res = make_request(f"{BASE_URL}/admin/users/{user_id}", "DELETE", headers=headers)

    if status == 200:
        print(f"{Colors.OKGREEN}✓ Delete request successful.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Delete failed: {del_res}{Colors.ENDC}")
        return

    # ---------------------------------------------------------
    # 6. Verify Deletion
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[6] Verifying Deletion (Expect 404)...{Colors.ENDC}")
    status, verify_res = make_request(f"{BASE_URL}/admin/users/{user_id}", "GET", headers=headers)

    if status == 404:
        print(f"{Colors.OKGREEN}✓ Verified: User not found (404).{Colors.ENDC}")
        print(f"\n{Colors.BOLD}🎉 All Admin User Management tests passed!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Error: User still exists or wrong status code ({status}).{Colors.ENDC}")

if __name__ == "__main__":
    run_test()
