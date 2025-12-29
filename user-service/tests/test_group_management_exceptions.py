#!/usr/bin/env python3
"""
Exception Test Script for Group Management Flow.
Tests all possible exception scenarios, edge cases, and error conditions.

This script tests:
- Invalid inputs and malformed data
- Unauthorized access attempts
- Boundary conditions and edge cases
- Server error scenarios
- Missing authentication
- Invalid identifiers and IDs
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
        return None, {"error": str(e)}

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
        return None

    user_id = reg_res['data']['user_id']

    status, active_res = make_request(
        f"{BASE_URL}/admin/users/{user_id}", "PUT", {"is_active": True}, admin_headers
    )

    if status != 200:
        print(f"{Colors.FAIL}❌ Activation failed: {active_res}{Colors.ENDC}")
        return None

    return {"id": user_id, "username": username, "email": email, "password": password}

def login_user(email, password):
    status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": email, "password": password
    })
    if status != 200:
        print(f"{Colors.FAIL}❌ Login failed for {email}{Colors.ENDC}")
        return None
    return login_res['data']['access_token']

def test_create_group_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing Group Creation Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user
    test_user = register_and_activate_user(admin_headers, "test_create")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test 1: Empty group name
    print(f"  1. Testing empty group name...")
    status, res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": ""}, headers)
    if status in [400, 422]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected empty group name (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for empty group name: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Very long group name
    print(f"  2. Testing very long group name...")
    long_name = "A" * 500
    status, res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": long_name}, headers)
    if status in [400, 413, 422]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected long group name (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for long group name: {status} - {res}{Colors.ENDC}")
    
    # Test 3: Missing group name field
    print(f"  3. Testing missing group name field...")
    status, res = make_request(f"{BASE_URL}/groups", "POST", {}, headers)
    if status in [400, 422]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected missing group name (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for missing group name: {status} - {res}{Colors.ENDC}")
    
    # Test 4: No authentication
    print(f"  4. Testing without authentication...")
    status, res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, {})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 5: Invalid token
    print(f"  5. Testing with invalid token...")
    invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
    status, res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, invalid_headers)
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid token (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid token: {status} - {res}{Colors.ENDC}")

def test_update_group_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing Group Update Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user and group
    test_user = register_and_activate_user(admin_headers, "test_update")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group first
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    # Test 1: Invalid group ID
    print(f"  1. Testing update with invalid group ID...")
    status, res = make_request(f"{BASE_URL}/groups/999999", "PUT", {"group_name": "Updated Name"}, headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid group ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid group ID: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Invalid group ID format
    print(f"  2. Testing update with invalid group ID format...")
    status, res = make_request(f"{BASE_URL}/groups/invalid_id", "PUT", {"group_name": "Updated Name"}, headers)
    if status in [400, 404]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid ID format (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid ID format: {status} - {res}{Colors.ENDC}")
    
    # Test 3: Empty group name
    print(f"  3. Testing update with empty group name...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}", "PUT", {"group_name": ""}, headers)
    if status in [400, 422]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected empty group name (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for empty group name: {status} - {res}{Colors.ENDC}")
    
    # Test 4: No authentication
    print(f"  4. Testing update without authentication...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}", "PUT", {"group_name": "Updated Name"}, {})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 5: Unauthorized access (different user)
    print(f"  5. Testing update by unauthorized user...")
    unauthorized_user = register_and_activate_user(admin_headers, "unauth_update")
    if unauthorized_user:
        unauth_token = login_user(unauthorized_user['email'], unauthorized_user['password'])
        unauth_headers = {"Authorization": f"Bearer {unauth_token}"} if unauth_token else {}
        status, res = make_request(f"{BASE_URL}/groups/{group_id}", "PUT", {"group_name": "Hacked Name"}, unauth_headers)
        if status in [403, 401]:
            print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthorized access (Status: {status}){Colors.ENDC}")
        else:
            print(f"    {Colors.WARNING}⚠ Unexpected response for unauthorized access: {status} - {res}{Colors.ENDC}")

def test_list_groups_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing List Groups Exceptions{Colors.ENDC}")
    
    # Test 1: No authentication
    print(f"  1. Testing list groups without authentication...")
    status, res = make_request(f"{BASE_URL}/groups", "GET", headers={})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Invalid token
    print(f"  2. Testing list groups with invalid token...")
    invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
    status, res = make_request(f"{BASE_URL}/groups", "GET", headers=invalid_headers)
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid token (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid token: {status} - {res}{Colors.ENDC}")

def test_add_member_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing Add Member Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test users and group
    test_user = register_and_activate_user(admin_headers, "test_add")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    member_user = register_and_activate_user(admin_headers, "member_add")
    if not member_user:
        print(f"{Colors.FAIL}❌ Failed to create member user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group first
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    # Test 1: Invalid group ID
    print(f"  1. Testing add member with invalid group ID...")
    status, res = make_request(f"{BASE_URL}/groups/999999/members", "POST", {"identifier": member_user['email']}, headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid group ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid group ID: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Invalid user identifier
    print(f"  2. Testing add member with invalid user identifier...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": "nonexistent@test.com"}, headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid user identifier (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid user identifier: {status} - {res}{Colors.ENDC}")
    
    # Test 3: Invalid group ID format
    print(f"  3. Testing add member with invalid group ID format...")
    status, res = make_request(f"{BASE_URL}/groups/invalid_id/members", "POST", {"identifier": member_user['email']}, headers)
    if status in [400, 404]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid ID format (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid ID format: {status} - {res}{Colors.ENDC}")
    
    # Test 4: No authentication
    print(f"  4. Testing add member without authentication...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": member_user['email']}, {})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 5: Adding user who is already a member
    print(f"  5. Testing adding user who is already a member...")
    # First add the member
    make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": member_user['email']}, headers)
    # Then try to add again
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": member_user['email']}, headers)
    if status in [400, 409]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected duplicate member addition (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for duplicate member: {status} - {res}{Colors.ENDC}")

def test_list_members_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing List Members Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user and group
    test_user = register_and_activate_user(admin_headers, "test_list")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group first
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    # Test 1: Invalid group ID
    print(f"  1. Testing list members with invalid group ID...")
    status, res = make_request(f"{BASE_URL}/groups/999999/members", "GET", headers=headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid group ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid group ID: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Invalid group ID format
    print(f"  2. Testing list members with invalid group ID format...")
    status, res = make_request(f"{BASE_URL}/groups/invalid_id/members", "GET", headers=headers)
    if status in [400, 404]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid ID format (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid ID format: {status} - {res}{Colors.ENDC}")
    
    # Test 3: No authentication
    print(f"  3. Testing list members without authentication...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members", "GET", headers={})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")

def test_get_member_profile_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing Get Member Profile Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test users and group
    test_user = register_and_activate_user(admin_headers, "test_profile")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    member_user = register_and_activate_user(admin_headers, "member_profile")
    if not member_user:
        print(f"{Colors.FAIL}❌ Failed to create member user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group and add member
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    # Add member to group
    make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": member_user['email']}, headers)
    
    # Test 1: Invalid group ID for identity profile
    print(f"  1. Testing get identity profile with invalid group ID...")
    status, res = make_request(f"{BASE_URL}/groups/999999/members/{member_user['id']}/identity-profile", "GET", headers=headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid group ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid group ID: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Invalid user ID for identity profile
    print(f"  2. Testing get identity profile with invalid user ID...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/999999/identity-profile", "GET", headers=headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid user ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid user ID: {status} - {res}{Colors.ENDC}")
    
    # Test 3: Invalid group ID format for health profile
    print(f"  3. Testing get health profile with invalid group ID format...")
    status, res = make_request(f"{BASE_URL}/groups/invalid_id/members/{member_user['id']}/health-profile", "GET", headers=headers)
    if status in [400, 404]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid ID format (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid ID format: {status} - {res}{Colors.ENDC}")
    
    # Test 4: No authentication for identity profile
    print(f"  4. Testing get identity profile without authentication...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/{member_user['id']}/identity-profile", "GET", headers={})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 5: User not in group for health profile
    print(f"  5. Testing get health profile for user not in group...")
    # Create another user not in the group
    outsider_user = register_and_activate_user(admin_headers, "outsider_profile")
    if outsider_user:
        status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/{outsider_user['id']}/health-profile", "GET", headers=headers)
        if status in [404, 403]:
            print(f"    {Colors.OKGREEN}✓ Correctly rejected request for user not in group (Status: {status}){Colors.ENDC}")
        else:
            print(f"    {Colors.WARNING}⚠ Unexpected response for user not in group: {status} - {res}{Colors.ENDC}")

def test_remove_member_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing Remove Member Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test users and group
    test_user = register_and_activate_user(admin_headers, "test_remove")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    member_user = register_and_activate_user(admin_headers, "member_remove")
    if not member_user:
        print(f"{Colors.FAIL}❌ Failed to create member user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group and add member
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    # Add member to group
    make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": member_user['email']}, headers)
    
    # Test 1: Invalid group ID
    print(f"  1. Testing remove member with invalid group ID...")
    status, res = make_request(f"{BASE_URL}/groups/999999/members/{member_user['id']}", "DELETE", headers=headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid group ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid group ID: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Invalid user ID
    print(f"  2. Testing remove member with invalid user ID...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/999999", "DELETE", headers=headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid user ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid user ID: {status} - {res}{Colors.ENDC}")
    
    # Test 3: Remove non-existent member
    print(f"  3. Testing remove member who is not in group...")
    # Create another user not in the group
    outsider_user = register_and_activate_user(admin_headers, "outsider_remove")
    if outsider_user:
        status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/{outsider_user['id']}", "DELETE", headers=headers)
        if status in [404, 400]:
            print(f"    {Colors.OKGREEN}✓ Correctly rejected removal of non-existent member (Status: {status}){Colors.ENDC}")
        else:
            print(f"    {Colors.WARNING}⚠ Unexpected response for non-existent member: {status} - {res}{Colors.ENDC}")
    
    # Test 4: No authentication
    print(f"  4. Testing remove member without authentication...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/{member_user['id']}", "DELETE", headers={})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 5: Unauthorized access (different user trying to remove)
    print(f"  5. Testing remove member by unauthorized user...")
    unauthorized_user = register_and_activate_user(admin_headers, "unauth_remove")
    if unauthorized_user:
        unauth_token = login_user(unauthorized_user['email'], unauthorized_user['password'])
        unauth_headers = {"Authorization": f"Bearer {unauth_token}"} if unauth_token else {}
        status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/{member_user['id']}", "DELETE", headers=unauth_headers)
        if status in [403, 401]:
            print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthorized access (Status: {status}){Colors.ENDC}")
        else:
            print(f"    {Colors.WARNING}⚠ Unexpected response for unauthorized access: {status} - {res}{Colors.ENDC}")

def test_update_member_role_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing Update Member Role Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test users and group
    test_user = register_and_activate_user(admin_headers, "test_role")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    member_user = register_and_activate_user(admin_headers, "member_role")
    if not member_user:
        print(f"{Colors.FAIL}❌ Failed to create member user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group and add member
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    # Add member to group
    make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": member_user['email']}, headers)
    
    # Test 1: Invalid group ID
    print(f"  1. Testing update member role with invalid group ID...")
    status, res = make_request(f"{BASE_URL}/groups/999999/members/{member_user['id']}", "PATCH", {"role": "head_chef"}, headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid group ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid group ID: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Invalid user ID
    print(f"  2. Testing update member role with invalid user ID...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/999999", "PATCH", {"role": "head_chef"}, headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid user ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid user ID: {status} - {res}{Colors.ENDC}")
    
    # Test 3: Invalid role
    print(f"  3. Testing update member role with invalid role...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/{member_user['id']}", "PATCH", {"role": "invalid_role"}, headers)
    if status in [400, 422]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid role (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid role: {status} - {res}{Colors.ENDC}")
    
    # Test 4: No authentication
    print(f"  4. Testing update member role without authentication...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/{member_user['id']}", "PATCH", {"role": "head_chef"}, {})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 5: Unauthorized access (different user trying to update role)
    print(f"  5. Testing update member role by unauthorized user...")
    unauthorized_user = register_and_activate_user(admin_headers, "unauth_role")
    if unauthorized_user:
        unauth_token = login_user(unauthorized_user['email'], unauthorized_user['password'])
        unauth_headers = {"Authorization": f"Bearer {unauth_token}"} if unauth_token else {}
        status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/{member_user['id']}", "PATCH", {"role": "head_chef"}, headers=unauth_headers)
        if status in [403, 401]:
            print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthorized access (Status: {status}){Colors.ENDC}")
        else:
            print(f"    {Colors.WARNING}⚠ Unexpected response for unauthorized access: {status} - {res}{Colors.ENDC}")

def test_leave_group_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing Leave Group Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user and group
    test_user = register_and_activate_user(admin_headers, "test_leave")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    # Test 1: Invalid group ID
    print(f"  1. Testing leave group with invalid group ID...")
    # We can't really test this directly since the endpoint is DELETE /groups/{id}/members/me
    # Instead, we'll test leaving a group that user is not in
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/me", "DELETE", headers=headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected leaving group user is not in (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for leaving group user is not in: {status} - {res}{Colors.ENDC}")
    
    # Test 2: No authentication
    print(f"  2. Testing leave group without authentication...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}/members/me", "DELETE", headers={})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 3: Valid scenario - user joins and then leaves
    print(f"  3. Testing valid leave group scenario...")
    # Add user to a group first
    other_user = register_and_activate_user(admin_headers, "other_leave")
    if other_user:
        other_token = login_user(other_user['email'], other_user['password'])
        other_headers = {"Authorization": f"Bearer {other_token}"} if other_token else {}
        
        # Create a group with other user
        status, other_group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Other Group"}, other_headers)
        if status == 201 and 'data' in other_group_res and 'id' in other_group_res['data']:
            other_group_id = other_group_res['data']['id']
            
            # Add test user to the group
            make_request(f"{BASE_URL}/groups/{other_group_id}/members", "POST", {"identifier": test_user['email']}, other_headers)
            
            # Now test user can leave
            test_user_token = login_user(test_user['email'], test_user['password'])
            test_user_headers = {"Authorization": f"Bearer {test_user_token}"} if test_user_token else {}
            status, res = make_request(f"{BASE_URL}/groups/{other_group_id}/members/me", "DELETE", headers=test_user_headers)
            if status in [200, 204]:
                print(f"    {Colors.OKGREEN}✓ Successfully left group (Status: {status}){Colors.ENDC}")
            else:
                print(f"    {Colors.WARNING}⚠ Unexpected response for leaving group: {status} - {res}{Colors.ENDC}")

def test_delete_group_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing Delete Group Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user and group
    test_user = register_and_activate_user(admin_headers, "test_delete")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group first
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    # Test 1: Invalid group ID
    print(f"  1. Testing delete group with invalid group ID...")
    status, res = make_request(f"{BASE_URL}/groups/999999", "DELETE", headers=headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid group ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid group ID: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Invalid group ID format
    print(f"  2. Testing delete group with invalid group ID format...")
    status, res = make_request(f"{BASE_URL}/groups/invalid_id", "DELETE", headers=headers)
    if status in [400, 404]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid ID format (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid ID format: {status} - {res}{Colors.ENDC}")
    
    # Test 3: No authentication
    print(f"  3. Testing delete group without authentication...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}", "DELETE", headers={})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 4: Unauthorized access (different user trying to delete)
    print(f"  4. Testing delete group by unauthorized user...")
    unauthorized_user = register_and_activate_user(admin_headers, "unauth_delete")
    if unauthorized_user:
        unauth_token = login_user(unauthorized_user['email'], unauthorized_user['password'])
        unauth_headers = {"Authorization": f"Bearer {unauth_token}"} if unauth_token else {}
        status, res = make_request(f"{BASE_URL}/groups/{group_id}", "DELETE", headers=unauth_headers)
        if status in [403, 401]:
            print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthorized access (Status: {status}){Colors.ENDC}")
        else:
            print(f"    {Colors.WARNING}⚠ Unexpected response for unauthorized access: {status} - {res}{Colors.ENDC}")

def test_get_group_exceptions():
    print(f"\n{Colors.BOLD}🧪 Testing Get Group Exceptions{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user and group
    test_user = register_and_activate_user(admin_headers, "test_get")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group first
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    # Test 1: Invalid group ID
    print(f"  1. Testing get group with invalid group ID...")
    status, res = make_request(f"{BASE_URL}/groups/999999", "GET", headers=headers)
    if status in [404, 400]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid group ID (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid group ID: {status} - {res}{Colors.ENDC}")
    
    # Test 2: Invalid group ID format
    print(f"  2. Testing get group with invalid group ID format...")
    status, res = make_request(f"{BASE_URL}/groups/invalid_id", "GET", headers=headers)
    if status in [400, 404]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected invalid ID format (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for invalid ID format: {status} - {res}{Colors.ENDC}")
    
    # Test 3: No authentication
    print(f"  3. Testing get group without authentication...")
    status, res = make_request(f"{BASE_URL}/groups/{group_id}", "GET", headers={})
    if status in [401, 403]:
        print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthenticated request (Status: {status}){Colors.ENDC}")
    else:
        print(f"    {Colors.WARNING}⚠ Unexpected response for unauthenticated request: {status} - {res}{Colors.ENDC}")
    
    # Test 4: Unauthorized access (user not in group)
    print(f"  4. Testing get group by unauthorized user...")
    unauthorized_user = register_and_activate_user(admin_headers, "unauth_get")
    if unauthorized_user:
        unauth_token = login_user(unauthorized_user['email'], unauthorized_user['password'])
        unauth_headers = {"Authorization": f"Bearer {unauth_token}"} if unauth_token else {}
        status, res = make_request(f"{BASE_URL}/groups/{group_id}", "GET", headers=unauth_headers)
        if status in [403, 401, 404]:
            print(f"    {Colors.OKGREEN}✓ Correctly rejected unauthorized access (Status: {status}){Colors.ENDC}")
        else:
            print(f"    {Colors.WARNING}⚠ Unexpected response for unauthorized access: {status} - {res}{Colors.ENDC}")

def run_exception_tests():
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Running Group Management Exception Tests{Colors.ENDC}")
    print(f"{Colors.INFO}Testing all possible exception scenarios and edge cases{Colors.ENDC}")
    
    test_create_group_exceptions()
    test_update_group_exceptions()
    test_list_groups_exceptions()
    test_add_member_exceptions()
    test_list_members_exceptions()
    test_get_member_profile_exceptions()
    test_remove_member_exceptions()
    test_update_member_role_exceptions()
    test_leave_group_exceptions()
    test_delete_group_exceptions()
    test_get_group_exceptions()
    
    print(f"\n{Colors.BOLD}🎉 Exception Testing Complete!{Colors.ENDC}")
    print(f"{Colors.INFO}All exception scenarios have been tested.{Colors.ENDC}")

if __name__ == "__main__":
    run_exception_tests()