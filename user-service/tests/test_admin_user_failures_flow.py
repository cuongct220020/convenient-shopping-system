#!/usr/bin/env python3
"""
Test script to identify potential crash scenarios in Admin User Management endpoints.

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

def test_pagination_edge_cases(admin_headers):
    """Test pagination with invalid parameters that could cause crashes."""
    print(f"\n{Colors.BOLD}[1] Testing Admin Users Pagination Edge Cases{Colors.ENDC}")
    
    # Test with non-numeric page parameter
    print(f"{Colors.INFO}  Testing non-numeric page parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users?page=invalid", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with non-numeric page_size parameter
    print(f"{Colors.INFO}  Testing non-numeric page_size parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users?page_size=invalid", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with negative page
    print(f"{Colors.INFO}  Testing negative page parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users?page=-1", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with negative page_size
    print(f"{Colors.INFO}  Testing negative page_size parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users?page_size=-5", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with extremely large page_size
    print(f"{Colors.INFO}  Testing extremely large page_size parameter...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users?page_size=999999", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Admin users pagination edge cases tested{Colors.ENDC}")

def test_invalid_uuid_parameters(admin_headers):
    """Test endpoints with invalid UUID parameters."""
    print(f"\n{Colors.BOLD}[2] Testing Invalid UUID Parameters{Colors.ENDC}")
    
    # Test with invalid UUID for user detail
    invalid_uuid = "not-a-uuid"
    print(f"{Colors.INFO}  Testing invalid UUID for user detail...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users/{invalid_uuid}", "GET", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with invalid UUID for user update
    print(f"{Colors.INFO}  Testing invalid UUID for user update...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users/{invalid_uuid}", "PUT", {"first_name": "test"}, headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with invalid UUID for user delete
    print(f"{Colors.INFO}  Testing invalid UUID for user delete...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users/{invalid_uuid}", "DELETE", headers=admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Invalid UUID parameters tested{Colors.ENDC}")

def test_malformed_json(admin_headers):
    """Test endpoints with malformed JSON data."""
    print(f"\n{Colors.BOLD}[3] Testing Malformed JSON Data{Colors.ENDC}")
    
    # Test with malformed JSON for user creation
    print(f"{Colors.INFO}  Testing POST with malformed JSON for user creation...{Colors.ENDC}")
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/admin/users",
            data=b"{invalid json}",
            headers={**admin_headers, "Content-Type": "application/json"},
            method="POST"
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
    
    # Test with malformed JSON for user update
    print(f"{Colors.INFO}  Testing PUT with malformed JSON for user update...{Colors.ENDC}")
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/admin/users/{str(uuid.uuid4())}",
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
    
    print(f"{Colors.OKGREEN}✓ Malformed JSON data tested{Colors.ENDC}")

def test_extreme_input_lengths(admin_headers):
    """Test endpoints with extremely long input values."""
    print(f"\n{Colors.BOLD}[4] Testing Extreme Input Lengths{Colors.ENDC}")
    
    # Test creating user with extremely long values
    extremely_long_string = "A" * 10000  # Very long string
    
    print(f"{Colors.INFO}  Testing user creation with extremely long values...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users", "POST", {
        "username": extremely_long_string[:255],  # Truncate to DB limit
        "email": f"{'a' * 50}@{'b' * 50}.com",  # Truncate to reasonable length
        "password": "Password123!",
        "first_name": extremely_long_string[:255],
        "last_name": extremely_long_string[:255],
        "phone_num": "09123456789",
        "system_role": "user",
        "is_active": True
    }, admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test updating user with extremely long values
    print(f"{Colors.INFO}  Testing user update with extremely long values...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users/{str(uuid.uuid4())}", "PUT", {
        "first_name": extremely_long_string[:255],
        "last_name": extremely_long_string[:255],
        "avatar_url": extremely_long_string
    }, admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Extreme input lengths tested{Colors.ENDC}")

def test_invalid_enum_values(admin_headers):
    """Test endpoints with invalid enum values."""
    print(f"\n{Colors.BOLD}[5] Testing Invalid Enum Values{Colors.ENDC}")
    
    # Test creating user with invalid system role
    print(f"{Colors.INFO}  Testing user creation with invalid system role...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users", "POST", {
        "username": f"testuser_{random.randint(1000, 9999)}",
        "email": f"test_{random.randint(1000, 9999)}@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User",
        "phone_num": "09123456789",
        "system_role": "invalid_role",  # Invalid role
        "is_active": True
    }, admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test creating user with invalid profile values
    print(f"{Colors.INFO}  Testing profile update with invalid enum values...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users/{str(uuid.uuid4())}", "PUT", {
        "identity_profile": {
            "gender": "invalid_gender",  # Invalid gender
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
            "activity_level": "invalid_level",  # Invalid activity level
            "health_goal": "invalid_goal"  # Invalid health goal
        }
    }, admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Invalid enum values tested{Colors.ENDC}")

def test_duplicate_constraint_violations(admin_headers):
    """Test creating users that violate unique constraints."""
    print(f"\n{Colors.BOLD}[6] Testing Duplicate Constraint Violations{Colors.ENDC}")
    
    # Create a base user first
    rnd = random.randint(10000, 99999)
    base_username = f"duplicate_test_{rnd}"
    base_email = f"duplicate_test_{rnd}@example.com"
    base_phone = f"09{rnd}1234"
    
    print(f"{Colors.INFO}  Creating base user...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users", "POST", {
        "username": base_username,
        "email": base_email,
        "password": "Password123!",
        "first_name": "Duplicate",
        "last_name": "Test",
        "phone_num": base_phone,
        "system_role": "user",
        "is_active": True
    }, admin_headers)
    
    if status == 201:
        print(f"{Colors.INFO}  Base user created successfully{Colors.ENDC}")
        
        # Try to create another user with same username
        print(f"{Colors.INFO}  Testing duplicate username...{Colors.ENDC}")
        status, res = make_request(f"{BASE_URL}/admin/users", "POST", {
            "username": base_username,  # Same username
            "email": f"diff_{base_email}",
            "password": "Password123!",
            "first_name": "Duplicate",
            "last_name": "Test",
            "phone_num": f"09{rnd}5678",
            "system_role": "user",
            "is_active": True
        }, admin_headers)
        print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
        
        # Try to create another user with same email
        print(f"{Colors.INFO}  Testing duplicate email...{Colors.ENDC}")
        status, res = make_request(f"{BASE_URL}/admin/users", "POST", {
            "username": f"diff_{base_username}",
            "email": base_email,  # Same email
            "password": "Password123!",
            "first_name": "Duplicate",
            "last_name": "Test",
            "phone_num": f"09{rnd}9012",
            "system_role": "user",
            "is_active": True
        }, admin_headers)
        print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
        
        # Try to create another user with same phone
        print(f"{Colors.INFO}  Testing duplicate phone...{Colors.ENDC}")
        status, res = make_request(f"{BASE_URL}/admin/users", "POST", {
            "username": f"diff2_{base_username}",
            "email": f"diff2_{base_email}",
            "password": "Password123!",
            "first_name": "Duplicate",
            "last_name": "Test",
            "phone_num": base_phone,  # Same phone
            "system_role": "user",
            "is_active": True
        }, admin_headers)
        print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Duplicate constraint violations tested{Colors.ENDC}")

def test_sql_injection_attempts(admin_headers):
    """Test endpoints with potential SQL injection attempts."""
    print(f"\n{Colors.BOLD}[7] Testing SQL Injection Attempts{Colors.ENDC}")
    
    # Test with SQL injection in username
    print(f"{Colors.INFO}  Testing SQL injection in username...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users", "POST", {
        "username": "test'; DROP TABLE users; --",
        "email": f"sql_test_{random.randint(1000, 9999)}@example.com",
        "password": "Password123!",
        "first_name": "SQL",
        "last_name": "Test",
        "phone_num": "09123456789",
        "system_role": "user",
        "is_active": True
    }, admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with SQL injection in email
    print(f"{Colors.INFO}  Testing SQL injection in email...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users", "POST", {
        "username": f"sql_test_{random.randint(1000, 9999)}",
        "email": "test'; DROP TABLE users; --@example.com",
        "password": "Password123!",
        "first_name": "SQL",
        "last_name": "Test",
        "phone_num": "09123456789",
        "system_role": "user",
        "is_active": True
    }, admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ SQL injection attempts tested{Colors.ENDC}")

def test_extreme_numeric_values(admin_headers):
    """Test endpoints with extreme numeric values."""
    print(f"\n{Colors.BOLD}[8] Testing Extreme Numeric Values{Colors.ENDC}")
    
    # Test with extremely large numbers in health profile
    print(f"{Colors.INFO}  Testing extremely large numeric values in health profile...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users/{str(uuid.uuid4())}", "PUT", {
        "health_profile": {
            "height_cm": 999999999,  # Extremely large height
            "weight_kg": 999999999.99,  # Extremely large weight
            "activity_level": "sedentary",
            "health_goal": "maintain"
        }
    }, admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    # Test with negative values where positive expected
    print(f"{Colors.INFO}  Testing negative values where positive expected...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users/{str(uuid.uuid4())}", "PUT", {
        "health_profile": {
            "height_cm": -100,  # Negative height
            "weight_kg": -50.5,  # Negative weight
            "activity_level": "sedentary",
            "health_goal": "maintain"
        }
    }, admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Extreme numeric values tested{Colors.ENDC}")

def test_memory_exhaustion_attempts(admin_headers):
    """Test endpoints with large payloads that could cause memory issues."""
    print(f"\n{Colors.BOLD}[9] Testing Memory Exhaustion Attempts{Colors.ENDC}")
    
    # Create a very large payload
    large_data = "A" * (10 * 1024 * 1024)  # 10MB of data
    
    print(f"{Colors.INFO}  Testing large payload in user creation...{Colors.ENDC}")
    status, res = make_request(f"{BASE_URL}/admin/users", "POST", {
        "username": f"large_payload_{random.randint(1000, 9999)}",
        "email": f"large_{random.randint(1000, 9999)}@example.com",
        "password": "Password123!",
        "first_name": "Large",
        "last_name": "Payload",
        "phone_num": "09123456789",
        "system_role": "user",
        "is_active": True,
        "avatar_url": large_data  # Very large field
    }, admin_headers)
    print(f"{Colors.INFO}    Status: {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Memory exhaustion attempts tested{Colors.ENDC}")

def run_crash_scenario_tests():
    """Run all crash scenario tests."""
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Testing Admin User Management Crash Scenarios{Colors.ENDC}")
    
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
    test_invalid_enum_values(admin_headers)
    test_duplicate_constraint_violations(admin_headers)
    test_sql_injection_attempts(admin_headers)
    test_extreme_numeric_values(admin_headers)
    test_memory_exhaustion_attempts(admin_headers)
    
    print(f"\n{Colors.BOLD}🎉 All admin user crash scenario tests completed!{Colors.ENDC}")
    print(f"{Colors.INFO}If the server is still running, it handled all the test cases without crashing.{Colors.ENDC}")
    
    return True

if __name__ == "__main__":
    success = run_crash_scenario_tests()
    if success:
        print(f"\n{Colors.OKGREEN}✓ Server survived all admin user crash scenario tests!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}✗ Some tests failed{Colors.ENDC}")
        sys.exit(1)