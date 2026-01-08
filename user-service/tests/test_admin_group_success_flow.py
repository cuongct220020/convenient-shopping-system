#!/usr/bin/env python3
"""
Script to test the full Admin Group Management Flow via Kong Gateway.

Scenario:
1. Login as Admin.
2. Create 2 normal users (User A, User B) via Admin API.
3. Create a Group (Admin creates via User API logic: POST /groups).
4. Update Group Info (via PUT /admin/groups/{id}).
5. List Groups (via GET /admin/groups).
6. Add User A & User B to Group (via POST /admin/groups/{id}/members).
7. List Group Members (via GET /admin/groups/{id}/members).
8. Promote User A to HEAD_CHEF (via PATCH /admin/groups/{id}/members/{user_id}).
9. Remove User B from Group (via DELETE /admin/groups/{id}/members/{user_id}).
10. Delete Group (via DELETE /admin/groups/{id}).
11. Verify Deletion.

Usage:
    python3 user-service/tests/test_admin_group_success_flow.py
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

# Admin Credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    INFO = '\033[94m'
    BOLD = '\033[1m'

def make_request(url, method="GET", data=None, headers=None):
    """Helper to make HTTP requests."""
    if headers is None: headers = {}
    
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
        try: return e.code, json.loads(body)
        except: return e.code, {"raw": body}
    except Exception as e:
        print(f"{Colors.FAIL}Connection Error to {url}: {e}{Colors.ENDC}")
        sys.exit(1)

def create_temp_user(admin_headers, tag):
    """Helper to create a temporary user via Admin API."""
    rnd = random.randint(10000, 99999)
    username = f"user_{tag}_{rnd}"
    email = f"user_{tag}_{rnd}@test.com"
    phone = f"09{rnd}{random.randint(1000,9999)}" # 11 chars max
    
    payload = {
        "username": username,
        "email": email,
        "password": "Password123!",
        "first_name": f"User{tag}",
        "last_name": "Test",
        "phone_num": phone,
        "is_active": True
    }
    
    status, res = make_request(f"{BASE_URL}/admin/users", "POST", payload, admin_headers)
    if status != 201:
        print(f"{Colors.FAIL}Failed to create temp user {tag}: {res}{Colors.ENDC}")
        sys.exit(1)
        
    return res['data']

def run_test():
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Testing Admin Group Management Flow (Full CRUD){Colors.ENDC}")
    
    # ---------------------------------------------------------
    # 0. Login as Admin
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[0] Logging in as Admin...{Colors.ENDC}")
    status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Admin Login failed.{Colors.ENDC}")
        sys.exit(1)

    admin_token = login_res['data']['access_token']
    headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"{Colors.OKGREEN}✓ Admin logged in.{Colors.ENDC}")

    # ---------------------------------------------------------
    # 1. Prepare Users
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[1] Creating Temporary Users (A & B)...{Colors.ENDC}")
    user_a = create_temp_user(headers, "A")
    user_b = create_temp_user(headers, "B")
    
    # User objects from Admin API return 'user_id' (based on UserCoreInfoSchema)
    id_a = user_a['user_id']
    id_b = user_b['user_id']
    print(f"{Colors.OKGREEN}✓ Created User A ({id_a}) and User B ({id_b}){Colors.ENDC}")

    # ---------------------------------------------------------
    # 2. Create Group (Using User API logic as Admin)
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[2] Creating Family Group (via User API)...{Colors.ENDC}")
    group_name_initial = f"Admin_Group_{random.randint(100,999)}"
    group_payload = {
        "group_name": group_name_initial,
        "group_avatar_url": "http://img.com/g.png"
    }
    # Using the standard user endpoint because Admin API doesn't have create group
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", group_payload, headers)
    
    if status != 201:
        print(f"{Colors.FAIL}❌ Create Group failed: {group_res}{Colors.ENDC}")
        return

    group_id = group_res['data']['id']
    print(f"{Colors.OKGREEN}✓ Group created. ID: {group_id}{Colors.ENDC}")

    # ---------------------------------------------------------
    # 3. Update Group Info (Admin API)
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[3] Updating Group Info via Admin API...{Colors.ENDC}")
    new_group_name = f"{group_name_initial}_UPDATED"
    update_payload = {"group_name": new_group_name}
    
    # PUT /admin/groups/{id}
    status, update_res = make_request(f"{BASE_URL}/admin/groups/{group_id}", "PUT", update_payload, headers)
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Update Group failed: {update_res}{Colors.ENDC}")
        return
        
    if update_res['data']['group_name'] == new_group_name:
        print(f"{Colors.OKGREEN}✓ Group name updated to '{new_group_name}'.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Group name mismatch!{Colors.ENDC}")

    # ---------------------------------------------------------
    # 4. List Groups (Admin API)
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[4] Listing Groups via Admin API...{Colors.ENDC}")
    # GET /admin/groups
    status, list_groups_res = make_request(f"{BASE_URL}/admin/groups?page=1&page_size=100", "GET", headers=headers)
    
    if status != 200:
        print(f"{Colors.FAIL}❌ List Groups failed: {list_groups_res}{Colors.ENDC}")
    else:
        # Check if our new group is in the list (inside 'data' array of pagination response)
        all_groups = list_groups_res['data']['data']
        found = any(g['id'] == group_id for g in all_groups)
        if found:
            print(f"{Colors.OKGREEN}✓ Verified group is in the admin list.{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ Created group not found in list!{Colors.ENDC}")

    # ---------------------------------------------------------
    # 5. Add Members (Admin API)
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[5] Adding User A & B via Admin API (Direct Add)...{Colors.ENDC}")
    
    # Add User A
    # POST /admin/groups/{id}/members. Payload: AddMemberRequestSchema (identifier)
    status, add_a = make_request(f"{BASE_URL}/admin/groups/{group_id}/members", "POST", {
        "identifier": user_a['email']
    }, headers)
    if status != 201:
        print(f"{Colors.FAIL}❌ Failed to add User A: {add_a}{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}✓ User A added.{Colors.ENDC}")

    # Add User B
    status, add_b = make_request(f"{BASE_URL}/admin/groups/{group_id}/members", "POST", {
        "identifier": user_b['email']
    }, headers)
    if status != 201:
        print(f"{Colors.FAIL}❌ Failed to add User B: {add_b}{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}✓ User B added.{Colors.ENDC}")

    # ---------------------------------------------------------
    # 6. List Members (Admin API)
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[6] Listing Members via Admin API...{Colors.ENDC}")
    status, list_res = make_request(f"{BASE_URL}/admin/groups/{group_id}/members", "GET", headers=headers)
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Failed to list members: {list_res}{Colors.ENDC}")
        return
        
    members = list_res['data']
    print(f"{Colors.INFO}    Found {len(members)} members.{Colors.ENDC}")
    
    # Verify User A and B are in the list. Structure: member['user']['user_id']
    member_ids = [m['user']['user_id'] for m in members]
    if id_a in member_ids and id_b in member_ids:
        print(f"{Colors.OKGREEN}✓ Verified User A and B are in the list.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Members missing from list!{Colors.ENDC}")

    # ---------------------------------------------------------
    # 7. Promote User A to HEAD_CHEF (Admin API)
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[7] Promoting User A to HEAD_CHEF...{Colors.ENDC}")
    # PATCH /admin/groups/{id}/members/{user_id}. Payload: GroupMembershipUpdateSchema (role)
    role_payload = {"role": "head_chef"}
    status, role_res = make_request(f"{BASE_URL}/admin/groups/{group_id}/members/{id_a}", "PATCH", role_payload, headers)
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Promote User A failed: {role_res}{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}✓ User A role updated to HEAD_CHEF.{Colors.ENDC}")

    # ---------------------------------------------------------
    # 8. Remove User B from Group (Admin API)
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[8] Removing User B via Admin API (Direct Remove)...{Colors.ENDC}")
    # DELETE /admin/groups/{id}/members/{uid}
    status, del_res = make_request(f"{BASE_URL}/admin/groups/{group_id}/members/{id_b}", "DELETE", headers=headers)
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Remove User B failed: {del_res}{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}✓ User B removed.{Colors.ENDC}")

    # Verify count
    status, verify_res = make_request(f"{BASE_URL}/admin/groups/{group_id}/members", "GET", headers=headers)
    members_after = verify_res['data']
    # Expect: Admin (Creator) + User A (Head Chef) = 2 members
    if len(members_after) == 2:
         print(f"{Colors.OKGREEN}✓ Member count verified (2).{Colors.ENDC}")
    else:
         print(f"{Colors.FAIL}⚠️ Warning: Member count is {len(members_after)}. Expected 2.{Colors.ENDC}")

    # ---------------------------------------------------------
    # 9. Delete Group
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[9] Deleting Group via Admin API...{Colors.ENDC}")
    status, del_group_res = make_request(f"{BASE_URL}/admin/groups/{group_id}", "DELETE", headers=headers)
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Delete Group failed: {del_group_res}{Colors.ENDC}")
        return
    print(f"{Colors.OKGREEN}✓ Group deleted.{Colors.ENDC}")

    # ---------------------------------------------------------
    # 10. Verify Deletion
    # ---------------------------------------------------------
    print(f"\n{Colors.BOLD}[10] Verifying Deletion...{Colors.ENDC}")
    status, verify_res = make_request(f"{BASE_URL}/admin/groups/{group_id}", "GET", headers=headers)
    
    if status == 404:
        print(f"{Colors.OKGREEN}✓ Verified: Group not found (404).{Colors.ENDC}")
        print(f"\n{Colors.BOLD}🎉 All Admin Group Management tests passed!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Error: Group still exists or wrong status ({status}).{Colors.ENDC}")

if __name__ == "__main__":
    run_test()
