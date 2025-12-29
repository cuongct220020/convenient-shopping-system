#!/usr/bin/env python3
"""
Server Crash & Error Handling Test Script for Group Management Flow.
Tests potential server crash scenarios and error handling edge cases.

This script tests:
- SQL injection attempts
- Buffer overflow attempts with extremely large inputs
- Malformed JSON payloads
- Rapid fire requests to test rate limiting
- Recursive/nested requests that might cause stack overflow
- Special character injection
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor

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
    CRITICAL = '\033[91m'

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

def test_sql_injection_attempts():
    print(f"\n{Colors.BOLD}💥 Testing SQL Injection Attempts{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user
    test_user = register_and_activate_user(admin_headers, "sql_test")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # SQL injection attempts in group name
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "'; EXEC xp_cmdshell 'ping 127.0.0.1'; --",
        "%27%20OR%20%271%27%3D%271",
        "' OR 1=1 --",
        "'; WAITFOR DELAY '00:00:05' --"
    ]
    
    for i, payload in enumerate(sql_payloads):
        print(f"  {i+1}. Testing SQL injection payload: {payload[:30]}...")
        status, res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": payload}, headers)
        # We expect these to be rejected, but the server should not crash
        if status in [400, 422, 500]:
            if status == 500:
                print(f"    {Colors.WARNING}⚠ Server returned 500 (internal error) - possible vulnerability: {status}{Colors.ENDC}")
            else:
                print(f"    {Colors.OKGREEN}✓ Request properly rejected (Status: {status}){Colors.ENDC}")
        else:
            print(f"    {Colors.CRITICAL}💥 CRITICAL: Payload may have been processed! Status: {status}{Colors.ENDC}")

def test_buffer_overflow_attempts():
    print(f"\n{Colors.BOLD}💥 Testing Buffer Overflow Attempts{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user
    test_user = register_and_activate_user(admin_headers, "buffer_test")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test extremely large inputs
    sizes = [1000, 5000, 10000, 50000, 100000]
    
    for size in sizes:
        print(f"  Testing with {size} character input...")
        large_input = "A" * size
        
        # Test large group name
        status, res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": large_input}, headers)
        if status is None:
            print(f"    {Colors.CRITICAL}💥 CRITICAL: Server may have crashed on {size} char input{Colors.ENDC}")
        elif status == 500:
            print(f"    {Colors.WARNING}⚠ Server returned 500 on {size} char input - possible buffer issue{Colors.ENDC}")
        else:
            print(f"    {Colors.OKGREEN}✓ Handled {size} char input properly (Status: {status}){Colors.ENDC}")
        
        # If server is still responsive, continue testing
        if status is not None:
            # Test large identifier in member addition
            status, res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Test Group"}, headers)
            if status == 201 and 'data' in res and 'id' in res['data']:
                group_id = res['data']['id']
                status, res = make_request(f"{BASE_URL}/groups/{group_id}/members", "POST", {"identifier": large_input}, headers)
                if status is None:
                    print(f"    {Colors.CRITICAL}💥 CRITICAL: Server may have crashed on member addition with large input{Colors.ENDC}")
                    break
                elif status == 500:
                    print(f"    {Colors.WARNING}⚠ Server returned 500 on large identifier - possible buffer issue{Colors.ENDC}")
                else:
                    print(f"    {Colors.OKGREEN}✓ Handled large identifier properly (Status: {status}){Colors.ENDC}")

def test_malformed_json():
    print(f"\n{Colors.BOLD}💥 Testing Malformed JSON Payloads{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user
    test_user = register_and_activate_user(admin_headers, "json_test")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Malformed JSON payloads
    malformed_payloads = [
        '{"group_name": "Test Group"',  # Missing closing brace
        '{"group_name": "Test Group",}',  # Trailing comma
        '{"group_name": }',  # Missing value
        '{"group_name": "Test Group", "extra_field": "value", "another_field": "value"}',  # Too many fields
        'group_name: Test Group',  # Not JSON at all
        '{"group_name": "Test Group", "group_name": "Duplicate"}',  # Duplicate keys
        '{group_name: "Test Group"}',  # Missing quotes
        '""',  # Empty string
        'null',  # Null value
        '["Test Group"]',  # Array instead of object
    ]
    
    headers_with_json = headers.copy()
    headers_with_json['Content-Type'] = 'application/json'
    
    for i, payload in enumerate(malformed_payloads):
        print(f"  {i+1}. Testing malformed JSON: {payload[:30]}...")
        
        # Create request manually to send malformed JSON
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            f"{BASE_URL}/groups",
            data=payload.encode('utf-8'),
            headers=headers_with_json,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                status = response.status
                res_data = response.read().decode('utf-8')
                res = json.loads(res_data) if res_data else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            try: 
                status, res = e.code, json.loads(body)
            except: 
                status, res = e.code, {"raw": body}
        except Exception as e:
            status, res = None, {"error": str(e)}
        
        if status is None:
            print(f"    {Colors.CRITICAL}💥 CRITICAL: Server may have crashed on malformed JSON{Colors.ENDC}")
        elif status == 500:
            print(f"    {Colors.WARNING}⚠ Server returned 500 on malformed JSON - possible vulnerability{Colors.ENDC}")
        else:
            print(f"    {Colors.OKGREEN}✓ Handled malformed JSON properly (Status: {status}){Colors.ENDC}")

def test_rapid_fire_requests():
    print(f"\n{Colors.BOLD}💥 Testing Rapid Fire Requests (Rate Limiting){Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user
    test_user = register_and_activate_user(admin_headers, "rapid_test")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Create a group first
    status, group_res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": "Rapid Test Group"}, headers)
    if status != 201 or 'data' not in group_res or 'id' not in group_res['data']:
        print(f"{Colors.FAIL}❌ Failed to create test group{Colors.ENDC}")
        return
    group_id = group_res['data']['id']
    
    def make_request_func():
        return make_request(f"{BASE_URL}/groups/{group_id}", "GET", headers=headers)
    
    # Send many requests in parallel
    print(f"  Sending 20 parallel requests...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request_func) for _ in range(20)]
        results = [future.result() for future in futures]
    
    # Check results
    statuses = [result[0] for result in results]
    status_counts = {}
    for status in statuses:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"    Status distribution: {status_counts}")
    
    if None in status_counts:
        print(f"    {Colors.CRITICAL}💥 CRITICAL: Some requests failed completely - server may be unstable{Colors.ENDC}")
    elif 500 in status_counts:
        print(f"    {Colors.WARNING}⚠ Server returned 500 errors under load - possible issues{Colors.ENDC}")
    else:
        print(f"    {Colors.OKGREEN}✓ Server handled parallel requests properly{Colors.ENDC}")

def test_special_character_injection():
    print(f"\n{Colors.BOLD}💥 Testing Special Character Injection{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user
    test_user = register_and_activate_user(admin_headers, "special_test")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Special character payloads
    special_chars = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "eval('alert(\"xss\")')",
        "{{7*7}}",  # Template injection
        "..\\..\\..\\windows\\system32\\",
        "/../../../etc/passwd",
        "file:///etc/passwd",
        "data:text/html,<script>alert('XSS')</script>",
        "'; --",
        "' OR '1'='1' /*",
        "<?php echo 'hacked'; ?>",
        "<img src=x onerror=alert('XSS')>",
        "${{7*7}}",
        "#{7*7}",
        "${7*7}",
        "%0A%0D%0A%0D",
        "\x00\x01\x02\x03",
        "NULL\x00BYTE",
        "∞∞∞∞∞∞∞∞∞∞",
        "‰‰‰‰‰‰‰‰‰‰",
        "¿‽⁇⁈⁉⁆⁇",
        "",
        "",
        "",
        "",
    ]
    
    for i, payload in enumerate(special_chars):
        print(f"  {i+1}. Testing special character payload: {repr(payload[:20])}...")
        status, res = make_request(f"{BASE_URL}/groups", "POST", {"group_name": payload}, headers)
        if status is None:
            print(f"    {Colors.CRITICAL}💥 CRITICAL: Server may have crashed on special character payload{Colors.ENDC}")
        elif status == 500:
            print(f"    {Colors.WARNING}⚠ Server returned 500 on special character - possible vulnerability{Colors.ENDC}")
        else:
            print(f"    {Colors.OKGREEN}✓ Handled special character properly (Status: {status}){Colors.ENDC}")

def test_recursive_structure():
    print(f"\n{Colors.BOLD}💥 Testing Recursive/Nested Structures{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user
    test_user = register_and_activate_user(admin_headers, "recursive_test")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Deeply nested JSON structure
    nested_data = {"level": 0}
    current = nested_data
    for i in range(100):  # Create 100 levels of nesting
        current["nested"] = {"level": i+1}
        current = current["nested"]
    
    print(f"  Testing deeply nested JSON structure (100 levels)...")
    status, res = make_request(f"{BASE_URL}/groups", "POST", nested_data, headers)
    if status is None:
        print(f"    {Colors.CRITICAL}💥 CRITICAL: Server may have crashed on nested structure{Colors.ENDC}")
    elif status == 500:
        print(f"    {Colors.WARNING}⚠ Server returned 500 on nested structure - possible stack overflow{Colors.ENDC}")
    else:
        print(f"    {Colors.OKGREEN}✓ Handled nested structure properly (Status: {status}){Colors.ENDC}")

def test_error_handling_consistency():
    print(f"\n{Colors.BOLD}💥 Testing Error Handling Consistency{Colors.ENDC}")
    
    # Admin login for user creation
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create test user
    test_user = register_and_activate_user(admin_headers, "error_test")
    if not test_user:
        print(f"{Colors.FAIL}❌ Failed to create test user{Colors.ENDC}")
        return
    
    token = login_user(test_user['email'], test_user['password'])
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test various error conditions and check if error responses are consistent
    error_scenarios = [
        ("Invalid Group ID", f"{BASE_URL}/groups/999999999999999999999", "GET", None, headers),
        ("Invalid Group ID Format", f"{BASE_URL}/groups/invalid_id_format_test", "GET", None, headers),
        ("Invalid Member ID", f"{BASE_URL}/groups/123/members/999999999999999999999", "GET", None, headers),
        ("Invalid Member ID Format", f"{BASE_URL}/groups/123/members/invalid_format", "GET", None, headers),
    ]
    
    for scenario_name, url, method, data, req_headers in error_scenarios:
        print(f"  Testing {scenario_name}...")
        status, res = make_request(url, method, data, req_headers)
        
        # Check if error response has proper structure
        has_error_field = 'error' in res or ('message' in res) or ('detail' in res)
        has_status_code = status is not None
        
        if status is None:
            print(f"    {Colors.CRITICAL}💥 CRITICAL: No response received - server may be unstable{Colors.ENDC}")
        elif status >= 500:
            print(f"    {Colors.WARNING}⚠ Server error (5xx) - possible unhandled exception: {status}{Colors.ENDC}")
        elif has_error_field and has_status_code:
            print(f"    {Colors.OKGREEN}✓ Proper error response structure (Status: {status}){Colors.ENDC}")
        else:
            print(f"    {Colors.WARNING}⚠ Inconsistent error handling (Status: {status}, Has error field: {has_error_field}){Colors.ENDC}")

def run_crash_tests():
    print(f"{Colors.HEADER}{Colors.BOLD}💥 Running Server Crash & Error Handling Tests{Colors.ENDC}")
    print(f"{Colors.INFO}Testing potential server vulnerabilities and error handling{Colors.ENDC}")
    
    test_sql_injection_attempts()
    test_buffer_overflow_attempts()
    test_malformed_json()
    test_rapid_fire_requests()
    test_special_character_injection()
    test_recursive_structure()
    test_error_handling_consistency()
    
    print(f"\n{Colors.BOLD}🎉 Crash Testing Complete!{Colors.ENDC}")
    print(f"{Colors.INFO}All crash scenarios have been tested. Check for any CRITICAL issues above.{Colors.ENDC}")

if __name__ == "__main__":
    run_crash_tests()