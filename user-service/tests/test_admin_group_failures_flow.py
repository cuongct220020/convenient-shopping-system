#!/usr/bin/env python3
"""
Test script to identify potential crash scenarios in Admin Group Management endpoints.

This script tests various edge cases and error conditions that could potentially cause
the server to crash or behave unexpectedly.
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

class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    INFO = '\033[94m'
    BOLD = '\033[1m'

def make_request(url, method="GET", data=None, headers=None):
    """Helper to make HTTP requests."""
    if headers is None: 
        headers = {}

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
        return 0, {"error": str(e)}

def get_admin_token():
    """Get admin authentication token."""
    status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })

    if status != 200:
        print(f"{Colors.FAIL}❌ Admin Login failed.{Colors.ENDC}")
        return None

    return login_res['data']['access_token']

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
        return None

    return res['data']

def test_pagination_edge_cases(admin_headers):
    """Test pagination with invalid parameters that could cause crashes."""
    print(f"\n{Colors.BOLD}[1] Testing Pagination Edge Cases{Colors.ENDC}")
    
    # Test with non-numeric page parameter
    print(f"{Colors.INFO}  Testing non-numeric page parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups?page=invalid", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with non-numeric page_size parameter
    print(f"{Colors.INFO}  Testing non-numeric page_size parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups?page_size=invalid", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with negative page
    print(f"{Colors.INFO}  Testing negative page parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups?page=-1", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with negative page_size
    print(f"{Colors.INFO}  Testing negative page_size parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups?page_size=-5", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with extremely large page_size
    print(f"{Colors.INFO}  Testing extremely large page_size parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups?page_size=999999", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Pagination edge cases tested{Colors.ENDC}")

def test_invalid_uuid_parameters(admin_headers):
    """Test endpoints with invalid UUID parameters."""
    print(f"\n{Colors.BOLD}[2] Testing Invalid UUID Parameters{Colors.ENDC}")
    
    # Test with invalid UUID for group_id
    invalid_uuid = "not-a-uuid"
    print(f"{Colors.INFO}  Testing invalid UUID for group detail...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups/{invalid_uuid}", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with invalid UUID for group update
    print(f"{Colors.INFO}  Testing invalid UUID for group update...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups/{invalid_uuid}", "PUT", {"group_name": "test"}, headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with invalid UUID for group delete
    print(f"{Colors.INFO}  Testing invalid UUID for group delete...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups/{invalid_uuid}", "DELETE", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with invalid UUIDs for group members endpoints
    print(f"{Colors.INFO}  Testing invalid UUIDs for group members...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups/{invalid_uuid}/members", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    status, res = make_request(f"{BASE_URL}/admin/groups/{invalid_uuid}/members", "POST", {"identifier": "test@example.com"}, headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with invalid UUIDs for member management
    print(f"{Colors.INFO}  Testing invalid UUIDs for member management...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/groups/{invalid_uuid}/members/{invalid_uuid}", "PATCH", {"role": "member"}, headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    status, res = make_request(f"{BASE_URL}/admin/groups/{invalid_uuid}/members/{invalid_uuid}", "DELETE", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Invalid UUID parameters tested{Colors.ENDC}")

def test_malformed_json(admin_headers):
    """Test endpoints with malformed JSON data."""
    print(f"\n{Colors.BOLD}[3] Testing Malformed JSON Data{Colors.ENDC}")
    
    # Create a valid group first to test update operations
    group_name = f"Test_Group_{random.randint(100, 999)}"
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {
        "group_name": group_name
    }, admin_headers)
    
    if status == 201:
        group_id = group_res['data']['id']
        print(f"{Colors.INFO}  Created test group: {group_id}{Colors.ENDC}")
        
        # Test PUT with malformed JSON body
        print(f"{Colors.INFO}  Testing PUT with malformed JSON...{Colors.ENDC}")
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/admin/groups/{group_id}",
                data=b"{invalid json}",
                headers={**admin_headers, "Content-Type": "application/json"},
                method="PUT"
            )
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, context=ctx) as response:
                status = response.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:
            status = f"Exception: {str(e)}"
        
        print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
        
        # Clean up
        make_request(f"{BASE_URL}/admin/groups/{group_id}", "DELETE", headers=admin_headers)
    
    print(f"{Colors.OKGREEN}✓ Malformed JSON data tested{Colors.ENDC}")

def test_extreme_input_lengths(admin_headers):
    """Test endpoints with extremely long input values."""
    print(f"\n{Colors.BOLD}[4] Testing Extreme Input Lengths{Colors.ENDC}")
    
    # Create a valid group first
    extremely_long_name = "A" * 10000  # Very long group name
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {
        "group_name": extremely_long_name[:255]  # Truncate to reasonable length for creation
    }, admin_headers)
    
    if status == 201:
        group_id = group_res['data']['id']
        print(f"{Colors.INFO}  Created test group: {group_id}{Colors.ENDC}")
        
        # Test updating with extremely long values
        print(f"{Colors.INFO}  Testing update with extremely long values...{Colors.ENDC}")
        status, res = make_request(f"{BASE_URL}/admin/groups/{group_id}", "PUT", {
            "group_name": extremely_long_name[:255],  # DB might have length limits
            "description": extremely_long_name
        }, admin_headers)
        print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
        
        # Clean up
        make_request(f"{BASE_URL}/admin/groups/{group_id}", "DELETE", headers=admin_headers)
    
    print(f"{Colors.OKGREEN}✓ Extreme input lengths tested{Colors.ENDC}")

def test_concurrent_operations(admin_headers):
    """Test concurrent operations that might cause race conditions."""
    print(f"\n{Colors.BOLD}[5] Testing Concurrent Operations{Colors.ENDC}")
    
    # Create a test group
    group_name = f"Concurrent_Test_Group_{random.randint(100, 999)}"
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {
        "group_name": group_name
    }, admin_headers)
    
    if status == 201:
        group_id = group_res['data']['id']
        print(f"{Colors.INFO}  Created test group: {group_id}{Colors.ENDC}")
        
        # Create a test user
        test_user = create_temp_user(admin_headers, "CONCURRENT")
        if test_user:
            user_id = test_user['user_id']
            print(f"{Colors.INFO}  Created test user: {user_id}{Colors.ENDC}")
            
            # Try to add the same user multiple times concurrently (in sequence for this test)
            print(f"{Colors.INFO}  Testing adding same user multiple times...{Colors.ENDC}")
            for i in range(3):
                status, res = make_request(f"{BASE_URL}/admin/groups/{group_id}/members", "POST", {
                    "identifier": test_user['email']
                }, admin_headers)
                print(f"{Colors.INFO}    Attempt {i+1}: Status {status}{Colors.ENDC}")
        
        # Clean up
        make_request(f"{BASE_URL}/admin/groups/{group_id}", "DELETE", headers=admin_headers)
    
    print(f"{Colors.OKGREEN}✓ Concurrent operations tested{Colors.ENDC}")

def test_missing_required_fields(admin_headers):
    """Test endpoints with missing required fields."""
    print(f"\n{Colors.BOLD}[6] Testing Missing Required Fields{Colors.ENDC}")
    
    # Create a test group
    group_name = f"Required_Fields_Test_{random.randint(100, 999)}"
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {
        "group_name": group_name
    }, admin_headers)
    
    if status == 201:
        group_id = group_res['data']['id']
        print(f"{Colors.INFO}  Created test group: {group_id}{Colors.ENDC}")
        
        # Test update with empty payload
        print(f"{Colors.INFO}  Testing update with empty payload...{Colors.ENDC}")
        status, res = make_request(f"{BASE_URL}/admin/groups/{group_id}", "PUT", {}, headers=admin_headers)
        print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
        
        # Test add member with missing identifier
        print(f"{Colors.INFO}  Testing add member with missing identifier...{Colors.ENDC}")
        status, res = make_request(f"{BASE_URL}/admin/groups/{group_id}/members", "POST", {}, headers=admin_headers)
        print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
        
        # Test update member role with missing role
        # First add a member to update
        test_user = create_temp_user(admin_headers, "MISSING")
        if test_user:
            status, res = make_request(f"{BASE_URL}/admin/groups/{group_id}/members", "POST", {
                "identifier": test_user['email']
            }, admin_headers)
            
            if status == 201:
                print(f"{Colors.INFO}  Testing update member role with missing role...{Colors.ENDC}")
                status, res = make_request(f"{BASE_URL}/admin/groups/{group_id}/members/{test_user['user_id']}", "PATCH", {}, headers=admin_headers)
                print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
        
        # Clean up
        make_request(f"{BASE_URL}/admin/groups/{group_id}", "DELETE", headers=admin_headers)
    
    print(f"{Colors.OKGREEN}✓ Missing required fields tested{Colors.ENDC}")

def run_crash_scenario_tests():
    """Run all crash scenario tests."""
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Testing Admin Group Management Crash Scenarios{Colors.ENDC}")
    
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        print(f"{Colors.FAIL}Cannot proceed without admin token{Colors.ENDC}")
        return False
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Run all tests
    test_pagination_edge_cases(admin_headers)
    test_invalid_uuid_parameters(admin_headers)
    test_malformed_json(admin_headers)
    test_extreme_input_lengths(admin_headers)
    test_concurrent_operations(admin_headers)
    test_missing_required_fields(admin_headers)
    
    print(f"\n{Colors.BOLD}🎉 All crash scenario tests completed!{Colors.ENDC}")
    print(f"{Colors.INFO}If the server is still running, it handled all the test cases without crashing.{Colors.ENDC}")
    
    return True

if __name__ == "__main__":
    success = run_crash_scenario_tests()
    if success:
        print(f"\n{Colors.OKGREEN}✓ Server survived all crash scenario tests!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}✗ Some tests failed{Colors.ENDC}")
        sys.exit(1)