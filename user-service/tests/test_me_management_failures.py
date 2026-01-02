#!/usr/bin/env python3
"""
Failure Test Script for /me Endpoints in the user-service.

This script tests failure scenarios, error conditions, and potential server crashes
for all /me endpoints:
1. Authentication failures
2. Invalid inputs and malformed data
3. Authorization failures
4. Server crash scenarios
5. Edge cases and boundary conditions

Usage:
    python3 user-service/tests/test_me_management_failures.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import time
import random
import string
from concurrent.futures import ThreadPoolExecutor

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
BASE_URL = f"{GATEWAY_URL}/api/v1/user-service"

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    INFO = '\033[94m'
    CRITICAL = '\033[91m'
    BOLD = '\033[1m'

def make_request(url, method="GET", data=None, headers=None, cookies=None):
    """Make an HTTP request with proper headers and error handling."""
    if headers is None:
        headers = {}

    if data and method in ["POST", "PUT", "PATCH"]:
        headers["Content-Type"] = "application/json"
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    if cookies:
        req.headers["Cookie"] = cookies

    # Create SSL context that doesn't verify certificates (for local development)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        response = urllib.request.urlopen(req, context=ssl_context)
        response_data = response.read().decode('utf-8')
        return {
            "status_code": response.getcode(),
            "data": json.loads(response_data) if response_data else None,
            "headers": dict(response.headers),
            "cookies": response.headers.get("Set-Cookie")
        }
    except urllib.error.HTTPError as e:
        response_data = e.read().decode('utf-8')
        return {
            "status_code": e.getcode(),
            "data": json.loads(response_data) if response_data else None,
            "headers": dict(e.headers),
            "error": str(e)
        }
    except urllib.error.URLError as e:
        return {
            "status_code": 0,
            "data": None,
            "error": f"URL Error: {str(e)}"
        }
    except Exception as e:
        return {
            "status_code": 0,
            "data": None,
            "error": f"Exception: {str(e)}"
        }

def print_status(step, status, details=""):
    """Print formatted status message."""
    if status == "SUCCESS":
        print(f"{Colors.OKGREEN}✓ {step}: {status}{Colors.ENDC}")
        if details:
            print(f"  Details: {details}")
    elif status == "FAILED":
        print(f"{Colors.FAIL}✗ {step}: {status}{Colors.ENDC}")
        if details:
            print(f"  Details: {details}")
    elif status == "INFO":
        print(f"{Colors.INFO}→ {step}: {details}{Colors.ENDC}")
    elif status == "CRITICAL":
        print(f"{Colors.CRITICAL}💥 {step}: {status}{Colors.ENDC}")
        if details:
            print(f"  Details: {details}")
    else:
        print(f"{Colors.WARNING}⚠ {step}: {status}{Colors.ENDC}")

def register_test_user():
    """Register a test user and return credentials."""
    test_username = f"testuser_{int(time.time())}_{random.randint(1000, 9999)}"
    test_email = f"test_{int(time.time())}@example.com"
    test_password = "SecurePassword123!"

    register_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "first_name": "Test",
        "last_name": "User"
    }

    response = make_request(
        f"{BASE_URL}/auth/register",
        method="POST",
        data=register_data
    )

    if response["status_code"] == 201:
        print_status("Test User Registration", "SUCCESS", f"User: {test_email}")
        return test_email, test_password
    else:
        print_status("Test User Registration", "FAILED", f"Status: {response['status_code']}")
        return None, None

def login_user(email, password):
    """Login user and return access token."""
    login_data = {"identifier": email, "password": password}

    response = make_request(
        f"{BASE_URL}/auth/login",
        method="POST",
        data=login_data
    )

    if response["status_code"] == 200:
        access_token = response["data"].get("data", {}).get("access_token")
        if access_token:
            return access_token
        else:
            print_status("Login", "FAILED", "No access token in response")
            return None
    else:
        print_status("Login", "FAILED", f"Status: {response['status_code']}")
        return None

def test_authentication_failures():
    """Test authentication failures for all /me endpoints."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Authentication Failures{Colors.ENDC}")
    print("=" * 60)

    # Test endpoints without authentication
    endpoints = [
        ("GET", "/users/me/"),
        ("PATCH", "/users/me"),
        ("GET", "/users/me/profile/identity"),
        ("PATCH", "/users/me/profile/identity"),
        ("GET", "/users/me/profile/health"),
        ("PATCH", "/users/me/profile/health"),
        ("POST", "/users/me/email/request-change"),
        ("POST", "/users/me/email/confirm-change"),
        ("POST", "/users/me/change-password"),
        ("GET", "/users/me/tags"),
        ("POST", "/users/me/tags"),
        ("PUT", "/users/me/tags/category/test"),
        ("POST", "/users/me/tags/delete")
    ]

    for method, endpoint in endpoints:
        print(f"\n{Colors.INFO}Testing {method} {endpoint} without authentication{Colors.ENDC}")
        response = make_request(f"{BASE_URL}{endpoint}", method=method, data={})
        
        if response["status_code"] in [401, 403]:
            print_status(f"{method} {endpoint}", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"{method} {endpoint}", "FAILED", f"Should return 401/403, got {response['status_code']}")

def test_invalid_token_failures():
    """Test failures with invalid/expired tokens."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Invalid Token Failures{Colors.ENDC}")
    print("=" * 60)

    # Test with invalid token format
    invalid_tokens = [
        "invalid_token",
        "Bearer ",
        "Bearer invalid_token",
        "Bearer " + "A" * 1000,  # Extremely long token
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid_payload.signature",  # Invalid JWT
        "",  # Empty token
        None,  # No token header
    ]

    endpoints = [
        ("GET", "/users/me/"),
        ("GET", "/users/me/profile/identity"),
        ("GET", "/users/me/profile/health"),
    ]

    for token in invalid_tokens:
        headers = {}
        if token:
            headers = {"Authorization": token if token.startswith("Bearer") else f"Bearer {token}"}
        
        for method, endpoint in endpoints:
            print(f"\n{Colors.INFO}Testing {method} {endpoint} with invalid token: {str(token)[:30]}...{Colors.ENDC}")
            response = make_request(f"{BASE_URL}{endpoint}", method=method, headers=headers, data={})
            
            if response["status_code"] in [401, 403]:
                print_status(f"Token '{str(token)[:10]}...'", "SUCCESS", f"{method} {endpoint} properly rejected (Status: {response['status_code']})")
            else:
                print_status(f"Token '{str(token)[:10]}...'", "FAILED", f"{method} {endpoint} should return 401/403, got {response['status_code']}")

def test_invalid_input_failures():
    """Test failures with invalid input data."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Invalid Input Failures{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    email, password = register_test_user()
    if not email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(email, password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test 1: Update user info with invalid data
    print(f"\n{Colors.INFO}Testing PATCH /users/me with invalid data{Colors.ENDC}")
    
    invalid_updates = [
        {"first_name": ""},  # Empty first name
        {"first_name": "A" * 1000},  # Extremely long first name
        {"last_name": ""},  # Empty last name
        {"last_name": "A" * 1000},  # Extremely long last name
        {"phone_num": "invalid_phone"},  # Invalid phone format
        {"phone_num": "123"},  # Too short phone
        {"phone_num": "A" * 100},  # Extremely long phone
        {"username": ""},  # Empty username (if allowed to update)
        {"username": "A" * 1000},  # Extremely long username
    ]

    for update_data in invalid_updates:
        response = make_request(
            f"{BASE_URL}/users/me",
            method="PATCH",
            headers=auth_headers,
            data=update_data
        )
        
        if response["status_code"] in [400, 422]:
            print_status(f"Invalid update: {list(update_data.keys())[0]}", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"Invalid update: {list(update_data.keys())[0]}", "FAILED", f"Should return 400/422, got {response['status_code']} - {response.get('data')}")

    # Test 2: Update identity profile with invalid data
    print(f"\n{Colors.INFO}Testing PATCH /users/me/profile/identity with invalid data{Colors.ENDC}")
    
    invalid_identity_data = [
        {"gender": "invalid_gender"},  # Invalid gender
        {"date_of_birth": "invalid_date"},  # Invalid date format
        {"date_of_birth": "2025-01-01"},  # Future date
        {"date_of_birth": "1800-01-01"},  # Too old date
        {"occupation": "A" * 1000},  # Extremely long occupation
        {"occupation": ""},  # Empty occupation
    ]

    for identity_data in invalid_identity_data:
        response = make_request(
            f"{BASE_URL}/users/me/profile/identity",
            method="PATCH",
            headers=auth_headers,
            data=identity_data
        )
        
        if response["status_code"] in [400, 422]:
            print_status(f"Invalid identity: {list(identity_data.keys())[0]}", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"Invalid identity: {list(identity_data.keys())[0]}", "FAILED", f"Should return 400/422, got {response['status_code']} - {response.get('data')}")

    # Test 3: Update health profile with invalid data
    print(f"\n{Colors.INFO}Testing PATCH /users/me/profile/health with invalid data{Colors.ENDC}")
    
    invalid_health_data = [
        {"height_cm": -100},  # Negative height
        {"height_cm": 9999},  # Extremely tall
        {"weight_kg": -50},  # Negative weight
        {"weight_kg": 9999},  # Extremely heavy
        {"activity_level": "invalid_level"},  # Invalid activity level
        {"curr_condition": "A" * 1000},  # Extremely long condition
        {"health_goal": "invalid_goal"},  # Invalid health goal
    ]

    for health_data in invalid_health_data:
        response = make_request(
            f"{BASE_URL}/users/me/profile/health",
            method="PATCH",
            headers=auth_headers,
            data=health_data
        )
        
        if response["status_code"] in [400, 422]:
            print_status(f"Invalid health: {list(health_data.keys())[0]}", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"Invalid health: {list(health_data.keys())[0]}", "FAILED", f"Should return 400/422, got {response['status_code']} - {response.get('data')}")

    # Test 4: Request email change with invalid data
    print(f"\n{Colors.INFO}Testing POST /users/me/email/request-change with invalid data{Colors.ENDC}")
    
    invalid_email_data = [
        {"new_email": "invalid_email"},  # Invalid email format
        {"new_email": ""},  # Empty email
        {"new_email": "a" * 300 + "@example.com"},  # Extremely long email
        {"new_email": "test@nonexistentdomainthatdoesnotexist12345.com"},  # Non-existent domain
    ]

    for email_data in invalid_email_data:
        response = make_request(
            f"{BASE_URL}/users/me/email/request-change",
            method="POST",
            headers=auth_headers,
            data=email_data
        )
        
        if response["status_code"] in [400, 422]:
            print_status(f"Invalid email: {list(email_data.keys())[0]}", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"Invalid email: {list(email_data.keys())[0]}", "FAILED", f"Should return 400/422, got {response['status_code']} - {response.get('data')}")

    # Test 5: Confirm email change with invalid data
    print(f"\n{Colors.INFO}Testing POST /users/me/email/confirm-change with invalid data{Colors.ENDC}")
    
    invalid_confirm_data = [
        {"new_email": "invalid_email", "otp_code": "123456"},  # Invalid email
        {"new_email": email, "otp_code": ""},  # Empty OTP
        {"new_email": email, "otp_code": "123"},  # Too short OTP
        {"new_email": email, "otp_code": "invalid_otp"},  # Invalid OTP format
        {"new_email": email, "otp_code": "999999"},  # Wrong OTP
    ]

    for confirm_data in invalid_confirm_data:
        response = make_request(
            f"{BASE_URL}/users/me/email/confirm-change",
            method="POST",
            headers=auth_headers,
            data=confirm_data
        )
        
        if response["status_code"] in [400, 422, 401]:
            print_status(f"Invalid confirm: {list(confirm_data.keys())[0]}", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"Invalid confirm: {list(confirm_data.keys())[0]}", "FAILED", f"Should return 400/422/401, got {response['status_code']} - {response.get('data')}")

    # Test 6: Change password with invalid data
    print(f"\n{Colors.INFO}Testing POST /users/me/change-password with invalid data{Colors.ENDC}")
    
    invalid_password_data = [
        {"current_password": "wrong_password", "new_password": "NewPassword123!"},  # Wrong current password
        {"current_password": "", "new_password": "NewPassword123!"},  # Empty current password
        {"current_password": password, "new_password": ""},  # Empty new password
        {"current_password": password, "new_password": "weak"},  # Weak new password
        {"current_password": password, "new_password": "123"},  # Very weak new password
        {"current_password": password, "new_password": password},  # Same as current password
    ]

    for password_data in invalid_password_data:
        response = make_request(
            f"{BASE_URL}/users/me/change-password",
            method="POST",
            headers=auth_headers,
            data=password_data
        )
        
        if response["status_code"] in [400, 422, 401]:
            print_status(f"Invalid password: {list(password_data.keys())[0]}", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"Invalid password: {list(password_data.keys())[0]}", "FAILED", f"Should return 400/422/401, got {response['status_code']} - {response.get('data')}")

def test_malformed_json():
    """Test endpoints with malformed JSON."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Malformed JSON{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    email, password = register_test_user()
    if not email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(email, password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}
    auth_headers["Content-Type"] = "application/json"

    # Malformed JSON payloads
    malformed_payloads = [
        '{"first_name": "Test"',  # Missing closing brace
        '{"first_name": "Test",}',  # Trailing comma
        '{"first_name": }',  # Missing value
        'first_name: Test',  # Not JSON at all
        '{"first_name": "Test", "first_name": "Duplicate"}',  # Duplicate keys
        '{first_name: "Test"}',  # Missing quotes
        '""',  # Empty string
        'null',  # Null value
        '["Test"]',  # Array instead of object
        '{"first_name": "Test", "extra_field": "value", "another_field": "value", "more_field": "value", "even_more": "value", "field5": "value", "field6": "value", "field7": "value", "field8": "value", "field9": "value", "field10": "value"}',  # Too many fields
    ]

    endpoints = [
        ("PATCH", "/users/me"),
        ("PATCH", "/users/me/profile/identity"),
        ("PATCH", "/users/me/profile/health"),
        ("POST", "/users/me/email/request-change"),
        ("POST", "/users/me/email/confirm-change"),
        ("POST", "/users/me/change-password"),
    ]

    for method, endpoint in endpoints:
        for i, payload in enumerate(malformed_payloads):
            print(f"\n{Colors.INFO}Testing {method} {endpoint} with malformed JSON {i+1}{Colors.ENDC}")
            
            # Create request manually to send malformed JSON
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                f"{BASE_URL}{endpoint}",
                data=payload.encode('utf-8'),
                headers=auth_headers,
                method=method
            )
            
            try:
                with urllib.request.urlopen(req, context=ctx) as response:
                    status = response.getcode()
                    res_data = response.read().decode('utf-8')
                    res = json.loads(res_data) if res_data else {}
            except urllib.error.HTTPError as e:
                body = e.read().decode('utf-8')
                try: 
                    status, res = e.getcode(), json.loads(body)
                except: 
                    status, res = e.getcode(), {"raw": body}
            except Exception as e:
                status, res = 0, {"error": str(e)}
            
            if status in [400, 422]:
                print_status(f"Malformed JSON {i+1}", "SUCCESS", f"{method} {endpoint} properly handled (Status: {status})")
            elif status >= 500:
                print_status(f"Malformed JSON {i+1}", "CRITICAL", f"{method} {endpoint} caused server error (Status: {status}) - potential crash vulnerability!")
            else:
                print_status(f"Malformed JSON {i+1}", "WARNING", f"{method} {endpoint} unexpected response (Status: {status})")

def test_sql_injection_attempts():
    """Test endpoints with SQL injection attempts."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing SQL Injection Attempts{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    email, password = register_test_user()
    if not email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(email, password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # SQL injection payloads
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "'; EXEC xp_cmdshell 'ping 127.0.0.1'; --",
        "%27%20OR%20%271%27%3D%271",
        "' OR 1=1 --",
        "'; WAITFOR DELAY '00:00:05' --",
        "' OR 'x'='x",
        "admin' --",
        "' OR 1=1 LIMIT 1 --",
        "'; SELECT SLEEP(5); --",
    ]

    # Test endpoints that accept user input
    test_cases = [
        ({"first_name": "Test", "last_name": payload}, "/users/me", "PATCH") for payload in sql_payloads[:3]
    ] + [
        ({"occupation": payload}, "/users/me/profile/identity", "PATCH") for payload in sql_payloads[:3]
    ] + [
        ({"curr_condition": payload}, "/users/me/profile/health", "PATCH") for payload in sql_payloads[:3]
    ]

    for data, endpoint, method in test_cases:
        print(f"\n{Colors.INFO}Testing {method} {endpoint} with SQL payload: {list(data.values())[0][:30]}...{Colors.ENDC}")
        response = make_request(
            f"{BASE_URL}{endpoint}",
            method=method,
            headers=auth_headers,
            data=data
        )
        
        if response["status_code"] in [400, 422]:
            print_status(f"SQL Payload: {list(data.values())[0][:20]}...", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        elif response["status_code"] >= 500:
            print_status(f"SQL Payload: {list(data.values())[0][:20]}...", "CRITICAL", f"Caused server error (Status: {response['status_code']}) - SQL injection vulnerability!")
        else:
            print_status(f"SQL Payload: {list(data.values())[0][:20]}...", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def test_buffer_overflow_attempts():
    """Test endpoints with buffer overflow attempts."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Buffer Overflow Attempts{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    email, password = register_test_user()
    if not email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(email, password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test with extremely large inputs
    sizes = [1000, 5000, 10000, 50000]
    
    for size in sizes:
        print(f"\n{Colors.INFO}Testing with {size} character inputs{Colors.ENDC}")
        
        large_first_name = "A" * size
        large_last_name = "B" * size
        large_occupation = "C" * size
        large_condition = "D" * size
        
        # Test updating user info with large inputs
        response = make_request(
            f"{BASE_URL}/users/me",
            method="PATCH",
            headers=auth_headers,
            data={"first_name": large_first_name, "last_name": large_last_name}
        )
        
        if response["status_code"] is None:
            print_status(f"Large input {size} chars", "CRITICAL", "Server may have crashed!")
        elif response["status_code"] >= 500:
            print_status(f"Large input {size} chars", "CRITICAL", f"Server returned 500 error (Status: {response['status_code']}) - possible buffer overflow!")
        elif response["status_code"] in [400, 413, 422]:
            print_status(f"Large input {size} chars", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"Large input {size} chars", "WARNING", f"Unexpected response (Status: {response['status_code']})")
        
        # Test identity profile with large inputs
        response = make_request(
            f"{BASE_URL}/users/me/profile/identity",
            method="PATCH",
            headers=auth_headers,
            data={"occupation": large_occupation}
        )
        
        if response["status_code"] is None:
            print_status(f"Large occupation {size} chars", "CRITICAL", "Server may have crashed!")
        elif response["status_code"] >= 500:
            print_status(f"Large occupation {size} chars", "CRITICAL", f"Server returned 500 error (Status: {response['status_code']}) - possible buffer overflow!")
        elif response["status_code"] in [400, 413, 422]:
            print_status(f"Large occupation {size} chars", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"Large occupation {size} chars", "WARNING", f"Unexpected response (Status: {response['status_code']})")
        
        # Test health profile with large inputs
        response = make_request(
            f"{BASE_URL}/users/me/profile/health",
            method="PATCH",
            headers=auth_headers,
            data={"curr_condition": large_condition}
        )
        
        if response["status_code"] is None:
            print_status(f"Large condition {size} chars", "CRITICAL", "Server may have crashed!")
        elif response["status_code"] >= 500:
            print_status(f"Large condition {size} chars", "CRITICAL", f"Server returned 500 error (Status: {response['status_code']}) - possible buffer overflow!")
        elif response["status_code"] in [400, 413, 422]:
            print_status(f"Large condition {size} chars", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"Large condition {size} chars", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def test_concurrent_requests():
    """Test server behavior under concurrent requests (potential crash scenario)."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Concurrent Requests{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    email, password = register_test_user()
    if not email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(email, password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    def make_concurrent_request():
        """Make a request to test endpoint."""
        response = make_request(
            f"{BASE_URL}/users/me",
            method="GET",
            headers=auth_headers
        )
        return response["status_code"]

    print(f"\n{Colors.INFO}Sending 20 concurrent requests to /users/me{Colors.ENDC}")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_concurrent_request) for _ in range(20)]
        results = [future.result() for future in futures]
    
    status_counts = {}
    for status in results:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print_status("Concurrent Requests", "INFO", f"Status distribution: {status_counts}")
    
    if 500 in status_counts or None in status_counts:
        print_status("Concurrent Requests", "CRITICAL", "Server returned 500 errors or no response under load - potential crash vulnerability!")
    elif 429 in status_counts:
        print_status("Concurrent Requests", "SUCCESS", "Server properly implemented rate limiting (429 responses)")
    else:
        print_status("Concurrent Requests", "INFO", "Server handled concurrent requests without crashing")

def test_special_character_injection():
    """Test endpoints with special character injection."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Special Character Injection{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    email, password = register_test_user()
    if not email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(email, password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

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

    # Test with special characters in various fields
    test_cases = [
        ({"first_name": payload}, "/users/me", "PATCH") for payload in special_chars[:5]
    ] + [
        ({"occupation": payload}, "/users/me/profile/identity", "PATCH") for payload in special_chars[:5]
    ] + [
        ({"curr_condition": payload}, "/users/me/profile/health", "PATCH") for payload in special_chars[:5]
    ]

    for data, endpoint, method in test_cases:
        print(f"\n{Colors.INFO}Testing {method} {endpoint} with special chars: {repr(list(data.values())[0][:20])}...{Colors.ENDC}")
        response = make_request(
            f"{BASE_URL}{endpoint}",
            method=method,
            headers=auth_headers,
            data=data
        )
        
        if response["status_code"] in [400, 422]:
            print_status(f"Special chars: {repr(list(data.values())[0][:15])}...", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        elif response["status_code"] >= 500:
            print_status(f"Special chars: {repr(list(data.values())[0][:15])}...", "CRITICAL", f"Caused server error (Status: {response['status_code']}) - potential injection vulnerability!")
        else:
            print_status(f"Special chars: {repr(list(data.values())[0][:15])}...", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def run_failure_tests():
    """Run all failure tests."""
    print(f"{Colors.HEADER}{Colors.BOLD}💥 Running /me Endpoints Failure Tests{Colors.ENDC}")
    print(f"{Colors.INFO}Testing failure scenarios, error conditions, and potential server crashes{Colors.ENDC}")
    
    test_authentication_failures()
    test_invalid_token_failures()
    test_invalid_input_failures()
    test_malformed_json()
    test_sql_injection_attempts()
    test_buffer_overflow_attempts()
    test_concurrent_requests()
    test_special_character_injection()
    
    print(f"\n{Colors.BOLD}🎉 Failure Testing Complete!{Colors.ENDC}")
    print(f"{Colors.INFO}Check for any CRITICAL issues above that indicate potential vulnerabilities or crashes.{Colors.ENDC}")

if __name__ == "__main__":
    run_failure_tests()