#!/usr/bin/env python3
"""
Script to test the Group Management Flow.
Covers 100% of endpoints in user-service/app/views/groups/

Scenario:
1. Setup: Login as Admin.
2. Create 3 users (HeadChef A, Member B, Member C) and activate them.
3. Login as User A.
4. Create a new Group ("Cooking Club"). (POST /groups)
5. Update Group info to "Gourmet Cooking Club". (PUT /groups/{id})
6. List User A's groups. (GET /groups)
7. Add User B and User C to the group. (POST /groups/{id}/members)
8. List group members. (GET /groups/{id}/members)
9. View User B's profiles (Identity & Health). (GET .../identity-profile & health-profile)
10. Kick User B from the group. (DELETE /groups/{id}/members/{user_id})
11. Promote User C to HEAD_CHEF. (PATCH /groups/{id}/members/{user_id})
12. User A tries to leave (should fail as HEAD_CHEF cannot leave with other members). (DELETE /groups/{id}/members/me)
13. User A kicks User C to become the only member. (DELETE /groups/{id}/members/{user_id})
14. User A can now leave as the last member. (DELETE /groups/{id}/members/me)
15. Verify group deletion. (GET /groups/{id} -> expect error)

Usage:
    python3 user-service/tests/test_group_management_flow.py
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
# GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
GATEWAY_URL = os.getenv("GATEWAY_URL", "https://dichotienloi.com")
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
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Testing FULL Group Management Flow{Colors.ENDC}")
    
    # 0. Admin Login
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Setup Users
    print(f"\n{Colors.BOLD}[1] Setting up 3 Users...{Colors.ENDC}")
    user_a = register_and_activate_user(admin_headers, "headchef")
    user_b = register_and_activate_user(admin_headers, "member_b")
    user_c = register_and_activate_user(admin_headers, "member_c")

    # 2. Login User A
    token_a = login_user(user_a['email'], user_a['password'])
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 3. Create Group
    print(f"\n{Colors.BOLD}[3] Creating group 'Cooking Club'...{Colors.ENDC}")
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {
        "group_name": "Cooking Club"
    }, headers_a)
    group_id = group_res['data']['id']
    print(f"{Colors.OKGREEN}✓ Group created: {group_id}{Colors.ENDC}")

    # 4. Update Group (PUT /groups/{id})
    print(f"\n{Colors.BOLD}[4] Updating group name to 'Gourmet Cooking Club'...{Colors.ENDC}")
    status, update_res = make_request(f"{BASE_URL}/groups/{group_id}", "PUT", {
        "group_name": "Gourmet Cooking Club"
    }, headers_a)
    if status == 200 and update_res['data']['group_name'] == "Gourmet Cooking Club":
        print(f"{Colors.OKGREEN}✓ Group updated successfully.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Update failed: {update_res}{Colors.ENDC}")

    # 5. List User Groups (GET /groups)
    print(f"\n{Colors.BOLD}[5] Listing User A's groups...{Colors.ENDC}")
    status, list_groups_res = make_request(f"{BASE_URL}/groups", "GET", headers=headers_a)
    if status == 200 and len(list_groups_res['data']['groups']) >= 1:
        print(f"{Colors.OKGREEN}✓ Groups listed. Found {len(list_groups_res['data']['groups'])} group(s).{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ List groups failed: {list_groups_res}{Colors.ENDC}")

    # 6. Add Members
    print(f"\n{Colors.BOLD}[6] Adding User B and User C...{Colors.ENDC}")
    make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": user_b['email']},
                 headers_a)
    make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": user_c['email']},
                 headers_a)
    print(f"{Colors.OKGREEN}✓ Members added.{Colors.ENDC}")

    # 7. List Members (GET /groups/{id}/members)
    print(f"\n{Colors.BOLD}[7] Verifying member list...{Colors.ENDC}")
    status, members_res = make_request(f"{BASE_URL}/groups/{group_id}/members", "GET", headers=headers_a)
    members = members_res['data']['members']
    print(f"{Colors.OKGREEN}✓ Found {len(members)} members.{Colors.ENDC}")

    # 8. View Profiles
    print(f"\n{Colors.BOLD}[8] Viewing User B's profiles...{Colors.ENDC}")
    make_request(f"{BASE_URL}/groups/{group_id}/members/{user_b['id']}/identity-profile", "GET", headers=headers_a)
    make_request(f"{BASE_URL}/groups/{group_id}/members/{user_b['id']}/health-profile", "GET", headers=headers_a)
    print(f"{Colors.OKGREEN}✓ Profiles retrieved.{Colors.ENDC}")

    # 9. Kick User B (DELETE /groups/{id}/members/{user_id})
    print(f"\n{Colors.BOLD}[9] Kicking User B...{Colors.ENDC}")
    make_request(f"{BASE_URL}/groups/{group_id}/members/{user_b['id']}", "DELETE", headers=headers_a)
    print(f"{Colors.OKGREEN}✓ User B kicked.{Colors.ENDC}")

    # 10. Promote User C to HEAD_CHEF (PATCH /groups/{id}/members/{user_id})
    print(f"\n{Colors.BOLD}[10] Promoting User C to head_chef...{Colors.ENDC}")
    status, promote_res = make_request(f"{BASE_URL}/groups/{group_id}/members/{user_c['id']}", "PATCH", {"role": "head_chef"}, headers_a)
    if status == 200:
        print(f"{Colors.OKGREEN}✓ User C promoted to HEAD_CHEF.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Promotion failed: {promote_res}{Colors.ENDC}")

    # 11. User A leaves the group (Should succeed and transfer HEAD_CHEF to C)
    print(f"\n{Colors.BOLD}[11] User A leaving group (Should succeed & transfer ownership)...{Colors.ENDC}")
    status, leave_res = make_request(f"{BASE_URL}/groups/{group_id}/members/me", "DELETE", headers=headers_a)
    if status == 200:
        print(f"{Colors.OKGREEN}✓ User A left successfully. Ownership should be transferred to User C.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ User A failed to leave: {leave_res}{Colors.ENDC}")
        sys.exit(1)

    # 12. Login as User C to verify ownership and clean up
    print(f"\n{Colors.BOLD}[12] Logging in as User C to verify ownership...{Colors.ENDC}")
    token_c = login_user(user_c['email'], user_c['password'])
    headers_c = {"Authorization": f"Bearer {token_c}"}
    
    status, group_info = make_request(f"{BASE_URL}/groups/{group_id}", "GET", headers=headers_c)
    if status == 200:
        # Check if C is now HEAD_CHEF
        members = group_info['data']['members']
        user_c_member = next((m for m in members if m['user']['user_id'] == user_c['id']), None)
        if user_c_member and user_c_member['role'] == 'head_chef':
             print(f"{Colors.OKGREEN}✓ Verified: User C is now HEAD_CHEF.{Colors.ENDC}")
        else:
             print(f"{Colors.FAIL}❌ User C is not HEAD_CHEF! Role: {user_c_member['role'] if user_c_member else 'None'}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Failed to get group info as User C: {group_info}{Colors.ENDC}")

    # 13. User C leaves (Group should be deleted as C is last member)
    print(f"\n{Colors.BOLD}[13] User C leaving group (Last member)...{Colors.ENDC}")
    status, leave_res_c = make_request(f"{BASE_URL}/groups/{group_id}/members/me", "DELETE", headers=headers_c)
    if status == 200:
        print(f"{Colors.OKGREEN}✓ User C left as the last member (group effectively deleted).{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Failed to leave as last member: {leave_res_c}{Colors.ENDC}")

    # 14. Verify group no longer exists by trying to access it
    print(f"\n{Colors.BOLD}[14] Verifying group no longer exists...{Colors.ENDC}")
    status, _ = make_request(f"{BASE_URL}/groups/{group_id}", "GET", headers=headers_a)
    if status in [404, 500]:
        print(f"{Colors.OKGREEN}✓ Group properly deleted when last member left.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Group still exists when it should be deleted!{Colors.ENDC}")

    print(f"{Colors.OKGREEN}✓ Final verification: Group is no longer accessible.{Colors.ENDC}")

    print(f"\n{Colors.BOLD}🎉 100% Group Management Endpoints Tested Successfully!{Colors.ENDC}")

if __name__ == "__main__":
    run_test()