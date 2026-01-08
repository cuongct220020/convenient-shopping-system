#!/usr/bin/env python3
"""
Script to test the Internal Group Access Check API Flow.
Target: POST /groups/internal/{group_id}/members/{user_id}/access-check

Scenarios covered:
1. Setup: Admin login, create users (HeadChef, Member, Outsider), create group.
2. Check Membership:
   - Success: User is a member (200 OK)
   - Failure: User is not a member (404 Not Found)
3. Check Head Chef Role:
   - Success: User is Head Chef (200 OK)
   - Failure: User is Member but NOT Head Chef (403 Forbidden)
   - Failure: User is not a member (404 Not Found)

Usage:
    python3 user-service/tests/test_internal_group_access_flow.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import random
import uuid

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
BASE_URL = f"{GATEWAY_URL}/api/v1/user-service"

# Admin Credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Colors
class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    INFO = '\033[94m'
    BOLD = '\033[1m'
    WARNING = '\033[93m'

def make_request(url, method="GET", data=None, headers=None):
    if headers is None: headers = {}
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    encoded_data = json.dumps(data).encode('utf-8') if data else None
    if data: headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            res_data = response.read().decode('utf-8')
            return response.status, json.loads(res_data) if res_data else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try: return e.code, json.loads(body)
        except: return e.code, {"raw": body}
    except Exception as e:
        print(f"{Colors.FAIL}Connection Error to {url}: {e}{Colors.ENDC}")
        sys.exit(1)

def register_and_activate_user(admin_headers, prefix):
    rnd = random.randint(10000, 99999)
    email = f"{prefix}_{rnd}@test.com"
    username = f"{prefix}_{rnd}"
    password = "UserPass123!"
    
    print(f"    Creating user: {username} ({email})...")
    
    status, reg_res = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": username, "email": email, "password": password,
        "first_name": prefix.capitalize(), "last_name": "User"
    })
    
    if status != 201:
        print(f"{Colors.FAIL}❌ Registration failed: {reg_res}{Colors.ENDC}")
        sys.exit(1)
        
    user_id = reg_res['data']['user_id']
    
    status, active_res = make_request(
        f"{BASE_URL}/admin/users/{user_id}", "PUT", {"is_active": True}, admin_headers
    )
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Activation failed: {active_res}{Colors.ENDC}")
        sys.exit(1)
        
    return {"id": user_id, "username": username, "email": email, "password": password}

def login_user(email, password):
    status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": email, "password": password
    })
    if status != 200:
        print(f"{Colors.FAIL}❌ Login failed for {email}{Colors.ENDC}")
        sys.exit(1)
    return login_res['data']['access_token']

def run_test():
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Testing Internal Group Access API Flow{Colors.ENDC}")
    print(f"{Colors.INFO}Target Endpoint: {BASE_URL}/groups/internal/{{group_id}}/members/{{user_id}}/access-check{Colors.ENDC}")
    
    # ---------------------------------------------------------
    # 0. Admin Login
    # ---------------------------------------------------------
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Admin Login failed. Run create_admin_user.py first.{Colors.ENDC}")
        sys.exit(1)

    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # ---------------------------------------------------------
    # 1. Setup Users
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[1] Setting up Users...{Colors.ENDC}")
    head_chef = register_and_activate_user(admin_headers, "headchef")
    member = register_and_activate_user(admin_headers, "member")
    outsider = register_and_activate_user(admin_headers, "outsider")

    # Login Head Chef to create group
    token_head_chef = login_user(head_chef['email'], head_chef['password'])
    headers_head_chef = {"Authorization": f"Bearer {token_head_chef}"}

    # ---------------------------------------------------------
    # 2. Create Group & Add Member
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[2] Creating Group & Adding Member...{Colors.ENDC}")
    
    # Create Group
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {
        "group_name": "Internal API Test Group"
    }, headers_head_chef)
    
    if status != 201:
        print(f"{Colors.FAIL}❌ Create Group failed.{Colors.ENDC}")
        sys.exit(1)
        
    group_id = group_res['data']['id']
    print(f"{Colors.OKGREEN}✓ Group created: {group_id}{Colors.ENDC}")

    # Add Member
    status, add_res = make_request(
        f"{BASE_URL}/groups/{group_id}/members", 
        "POST", 
        {"identifier": member['email']},
        headers_head_chef
    )
    
    if status != 201:
        print(f"{Colors.FAIL}❌ Add Member failed.{Colors.ENDC}")
        sys.exit(1)
    print(f"{Colors.OKGREEN}✓ Member added: {member['email']}{Colors.ENDC}")

    # ---------------------------------------------------------
    # Helper for Internal Request
    # ---------------------------------------------------------
    def check_access(g_id, u_id, check_head_chef):
        url = f"{BASE_URL}/groups/internal/{g_id}/members/{u_id}/access-check"
        payload = {"check_head_chef": check_head_chef}
        # No Authorization header needed for internal API (based on our allowlist config)
        return make_request(url, "POST", payload, headers={})

    # ---------------------------------------------------------
    # 3. Test Cases: Membership Check
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[3] Testing Basic Membership Check (check_head_chef=False){Colors.ENDC}")

    # Case 3.1: Member (Success)
    print(f"  3.1 Checking actual member...")
    status, res = check_access(group_id, member['id'], False)
    if status == 200 and res['data']['authorized'] is True:
        print(f"    {Colors.OKGREEN}✓ Success: Member authorized (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.FAIL}❌ Failed: Member should be authorized. Got: {res}{Colors.ENDC}")

    # Case 3.2: Head Chef (Success - implied member)
    print(f"  3.2 Checking Head Chef (as member)...")
    status, res = check_access(group_id, head_chef['id'], False)
    if status == 200 and res['data']['authorized'] is True:
        print(f"    {Colors.OKGREEN}✓ Success: Head Chef authorized as member (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.FAIL}❌ Failed: Head Chef should be authorized. Got: {res}{Colors.ENDC}")

    # Case 3.3: Outsider (Failure)
    print(f"  3.3 Checking outsider (non-member)...")
    status, res = check_access(group_id, outsider['id'], False)
    if status == 404:
        print(f"    {Colors.OKGREEN}✓ Success: Outsider rejected (Status: 404){Colors.ENDC}")
    else:
        print(f"    {Colors.FAIL}❌ Failed: Outsider should get 404. Got: {status}{Colors.ENDC}")

    # ---------------------------------------------------------
    # 4. Test Cases: Head Chef Role Check
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[4] Testing Head Chef Role Check (check_head_chef=True){Colors.ENDC}")

    # Case 4.1: Head Chef (Success)
    print(f"  4.1 Checking Head Chef...")
    status, res = check_access(group_id, head_chef['id'], True)
    if status == 200 and res['data']['is_head_chef'] is True:
        print(f"    {Colors.OKGREEN}✓ Success: Head Chef authorized (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.FAIL}❌ Failed: Head Chef should be authorized. Got: {res}{Colors.ENDC}")

    # Case 4.2: Member (Forbidden - is member but not HC)
    print(f"  4.2 Checking regular Member (expecting Forbidden)...")
    status, res = check_access(group_id, member['id'], True)
    if status == 403:
        print(f"    {Colors.OKGREEN}✓ Success: Member rejected as Head Chef (Status: 403){Colors.ENDC}")
    else:
        print(f"    {Colors.FAIL}❌ Failed: Member should get 403. Got: {status} - {res}{Colors.ENDC}")

    # Case 4.3: Outsider (Not Found)
    print(f"  4.3 Checking Outsider (expecting Not Found)...")
    status, res = check_access(group_id, outsider['id'], True)
    if status == 404:
        print(f"    {Colors.OKGREEN}✓ Success: Outsider rejected (Status: 404){Colors.ENDC}")
    else:
        print(f"    {Colors.FAIL}❌ Failed: Outsider should get 404. Got: {status}{Colors.ENDC}")

    # ---------------------------------------------------------
    # 5. Test Cases: Edge Cases
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[5] Testing Edge Cases{Colors.ENDC}")

    # Case 5.1: Invalid Group UUID
    print(f"  5.1 Invalid Group UUID...")
    status, res = check_access("invalid-uuid", member['id'], False)
    # Sanic UUID converter usually returns 404 or 400 for bad format before reaching view
    if status in [404, 400]: 
        print(f"    {Colors.OKGREEN}✓ Success: Invalid UUID handled (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Warning: Unexpected status for invalid UUID: {status}{Colors.ENDC}")

    # Case 5.2: Non-existent Group UUID
    print(f"  5.2 Non-existent Group UUID...")
    fake_uuid = str(uuid.uuid4())
    status, res = check_access(fake_uuid, member['id'], False)
    if status == 404:
        print(f"    {Colors.OKGREEN}✓ Success: Non-existent group returns 404{Colors.ENDC}")
    else:
        print(f"    {Colors.FAIL}❌ Failed: Should be 404. Got: {status}{Colors.ENDC}")

    print(f"\n{Colors.BOLD}🎉 Internal API Tests Completed!{Colors.ENDC}")

if __name__ == "__main__":
    run_test()
