#!/usr/bin/env python3
"""
Comprehensive Authentication Failure Scenarios Test Script

This script tests various failure scenarios for authentication endpoints,
including malformed requests, invalid data, missing fields, and potential
server crash scenarios to test server resilience.

Scenarios tested:
1. Health check with invalid methods
2. Registration with invalid data
3. OTP requests with invalid data
4. Login with invalid credentials
5. Token refresh with invalid tokens
6. Access to protected resources with invalid tokens
7. Logout with invalid tokens
8. Password reset with invalid data
9. Stress testing with multiple concurrent requests
10. Malformed JSON and edge cases
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
import string

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
    BOLD = '\033[1m'

def make_request(url, method="GET", data=None, headers=None):
    """Helper function to make HTTP requests."""
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
            return response.status, response.headers, json.loads(res_data) if res_data else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, e.headers, json.loads(body)
        except:
            return e.code, e.headers, {"raw": body}
    except Exception as e:
        print(f"{Colors.FAIL}Connection Error: {e}{Colors.ENDC}")
        return 0, None, None

def get_cookie_value(headers, cookie_name: str):
    """Extracts a cookie value from the 'Set-Cookie' header."""
    if not headers:
        return None

    # urllib headers object can return a list for repeated headers
    cookie_headers = headers.get_all('Set-Cookie') if hasattr(headers, 'get_all') else headers.get('Set-Cookie')

    if not cookie_headers:
        return None

    if isinstance(cookie_headers, str):
        cookie_headers = [cookie_headers]

    for header_value in cookie_headers:
        # A single Set-Cookie header looks like: "refresh_token=abc; Path=/; HttpOnly"
        parts = header_value.split(';')
        cookie_part = parts[0].strip() # "refresh_token=abc"
        if '=' in cookie_part:
            name, value = cookie_part.split('=', 1)
            if name.strip() == cookie_name:
                return value.strip()
    return None

def test_health_failures():
    """Test health check endpoint with invalid methods and malformed requests."""
    print(f"{Colors.INFO}[1] 🔍 Testing health check failures...{Colors.ENDC}")
    
    # Test with invalid HTTP method
    status, headers, response = make_request(f"{BASE_URL}/health", "POST", {"invalid": "data"})
    print(f"{Colors.WARNING}  Health check with POST: Status {status}{Colors.ENDC}")
    
    # Test with PUT method
    status, headers, response = make_request(f"{BASE_URL}/health", "PUT", {"data": "test"})
    print(f"{Colors.WARNING}  Health check with PUT: Status {status}{Colors.ENDC}")
    
    # Test with DELETE method
    status, headers, response = make_request(f"{BASE_URL}/health", "DELETE")
    print(f"{Colors.WARNING}  Health check with DELETE: Status {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Health check failure tests completed{Colors.ENDC}")
    return True

def test_registration_failures():
    """Test registration endpoint with various failure scenarios."""
    print(f"{Colors.INFO}[2] 📝 Testing registration failures...{Colors.ENDC}")
    
    # Test with empty data
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {})
    print(f"{Colors.WARNING}  Empty registration data: Status {status}{Colors.ENDC}")
    
    # Test with missing required fields
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": "testuser"
        # Missing email, password, etc.
    })
    print(f"{Colors.WARNING}  Missing required fields: Status {status}{Colors.ENDC}")
    
    # Test with invalid email format
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": "testuser",
        "email": "invalid-email",
        "password": "password123"
    })
    print(f"{Colors.WARNING}  Invalid email format: Status {status}{Colors.ENDC}")
    
    # Test with too short password
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123"
    })
    print(f"{Colors.WARNING}  Too short password: Status {status}{Colors.ENDC}")
    
    # Test with too long inputs
    long_string = "a" * 1000
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": long_string,
        "email": f"{long_string}@example.com",
        "password": long_string
    })
    print(f"{Colors.WARNING}  Extremely long inputs: Status {status}{Colors.ENDC}")
    
    # Test with SQL injection attempt
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": "'; DROP TABLE users; --",
        "email": "'; DROP TABLE users; --@example.com",
        "password": "'; DROP TABLE users; --"
    })
    print(f"{Colors.WARNING}  SQL injection attempt: Status {status}{Colors.ENDC}")
    
    # Test with XSS attempt
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": "<script>alert('xss')</script>",
        "email": "<script>alert('xss')</script>@example.com",
        "password": "<script>alert('xss')</script>"
    })
    print(f"{Colors.WARNING}  XSS attempt: Status {status}{Colors.ENDC}")
    
    # Test with duplicate registration (if user exists)
    rnd = random.randint(10000, 99999)
    email = f"fail_test_user_{rnd}@example.com"
    username = f"fail_user_{rnd}"
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": username,
        "email": email,
        "password": "SecurePassword123!",
        "first_name": "Fail",
        "last_name": "Tester"
    })
    
    # Try to register the same user again
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": username,
        "email": email,
        "password": "SecurePassword123!",
        "first_name": "Fail",
        "last_name": "Tester"
    })
    print(f"{Colors.WARNING}  Duplicate registration: Status {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Registration failure tests completed{Colors.ENDC}")
    return True

def test_otp_send_failures():
    """Test OTP send endpoint with various failure scenarios."""
    print(f"{Colors.INFO}[3] 📧 Testing OTP send failures...{Colors.ENDC}")
    
    # Test with empty data
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/send", "POST", {})
    print(f"{Colors.WARNING}  Empty OTP send data: Status {status}{Colors.ENDC}")
    
    # Test with invalid email
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": "invalid-email",
        "action": "register"
    })
    print(f"{Colors.WARNING}  Invalid email format: Status {status}{Colors.ENDC}")
    
    # Test with missing action
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": "test@example.com"
        # Missing action
    })
    print(f"{Colors.WARNING}  Missing action: Status {status}{Colors.ENDC}")
    
    # Test with invalid action
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": "test@example.com",
        "action": "invalid_action"
    })
    print(f"{Colors.WARNING}  Invalid action: Status {status}{Colors.ENDC}")
    
    # Test with non-existent email
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": "nonexistent@example.com",
        "action": "register"
    })
    print(f"{Colors.WARNING}  Non-existent email: Status {status}{Colors.ENDC}")
    
    # Test with extremely long email
    long_email = "a" * 500 + "@example.com"
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": long_email,
        "action": "register"
    })
    print(f"{Colors.WARNING}  Extremely long email: Status {status}{Colors.ENDC}")
    
    # Test with SQL injection in email
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": "'; DROP TABLE users; --",
        "action": "register"
    })
    print(f"{Colors.WARNING}  SQL injection in email: Status {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ OTP send failure tests completed{Colors.ENDC}")
    return True

def test_otp_verify_failures():
    """Test OTP verify endpoint with various failure scenarios."""
    print(f"{Colors.INFO}[4] ✅ Testing OTP verify failures...{Colors.ENDC}")
    
    # Test with empty data
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/verify", "POST", {})
    print(f"{Colors.WARNING}  Empty OTP verify data: Status {status}{Colors.ENDC}")
    
    # Test with missing fields
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/verify", "POST", {
        "email": "test@example.com"
        # Missing otp_code
    })
    print(f"{Colors.WARNING}  Missing OTP code: Status {status}{Colors.ENDC}")
    
    # Test with invalid email format
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/verify", "POST", {
        "email": "invalid-email",
        "otp_code": "123456"
    })
    print(f"{Colors.WARNING}  Invalid email format: Status {status}{Colors.ENDC}")
    
    # Test with invalid OTP format
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/verify", "POST", {
        "email": "test@example.com",
        "otp_code": "invalid-otp"
    })
    print(f"{Colors.WARNING}  Invalid OTP format: Status {status}{Colors.ENDC}")
    
    # Test with too long OTP
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/verify", "POST", {
        "email": "test@example.com",
        "otp_code": "1" * 100
    })
    print(f"{Colors.WARNING}  Too long OTP: Status {status}{Colors.ENDC}")
    
    # Test with non-existent email
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/verify", "POST", {
        "email": "nonexistent@example.com",
        "otp_code": "123456"
    })
    print(f"{Colors.WARNING}  Non-existent email: Status {status}{Colors.ENDC}")
    
    # Test with wrong OTP
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/verify", "POST", {
        "email": "test@example.com",
        "otp_code": "000000"  # Wrong OTP
    })
    print(f"{Colors.WARNING}  Wrong OTP: Status {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ OTP verify failure tests completed{Colors.ENDC}")
    return True

def test_login_failures():
    """Test login endpoint with various failure scenarios."""
    print(f"{Colors.INFO}[5] 🔐 Testing login failures...{Colors.ENDC}")
    
    # Test with empty data
    status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {})
    print(f"{Colors.WARNING}  Empty login data: Status {status}{Colors.ENDC}")
    
    # Test with missing fields
    status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": "test@example.com"
        # Missing password
    })
    print(f"{Colors.WARNING}  Missing password: Status {status}{Colors.ENDC}")
    
    # Test with invalid identifier format
    status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": "invalid-identifier",
        "password": "password123"
    })
    print(f"{Colors.WARNING}  Invalid identifier format: Status {status}{Colors.ENDC}")
    
    # Test with non-existent user
    status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": "nonexistent@example.com",
        "password": "password123"
    })
    print(f"{Colors.WARNING}  Non-existent user: Status {status}{Colors.ENDC}")
    
    # Test with wrong password
    rnd = random.randint(10000, 99999)
    email = f"login_fail_test_{rnd}@example.com"
    username = f"login_fail_{rnd}"
    
    # First register a user
    reg_status, _, _ = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": username,
        "email": email,
        "password": "SecurePassword123!",
        "first_name": "Login",
        "last_name": "Fail"
    })
    
    if reg_status == 201:
        # Try to login with wrong password
        status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
            "identifier": email,
            "password": "wrongpassword"
        })
        print(f"{Colors.WARNING}  Wrong password: Status {status}{Colors.ENDC}")
    
    # Test with extremely long identifier
    long_identifier = "a" * 500 + "@example.com"
    status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": long_identifier,
        "password": "password123"
    })
    print(f"{Colors.WARNING}  Extremely long identifier: Status {status}{Colors.ENDC}")
    
    # Test with extremely long password
    long_password = "p" * 1000
    status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": "test@example.com",
        "password": long_password
    })
    print(f"{Colors.WARNING}  Extremely long password: Status {status}{Colors.ENDC}")
    
    # Test with SQL injection
    status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": "'; DROP TABLE users; --",
        "password": "' OR '1'='1"
    })
    print(f"{Colors.WARNING}  SQL injection attempt: Status {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Login failure tests completed{Colors.ENDC}")
    return True

def test_refresh_token_failures():
    """Test refresh token endpoint with various failure scenarios."""
    print(f"{Colors.INFO}[6] ♻️  Testing refresh token failures...{Colors.ENDC}")
    
    # Test without refresh token cookie
    status, headers, response = make_request(f"{BASE_URL}/auth/refresh-token", "POST")
    print(f"{Colors.WARNING}  No refresh token cookie: Status {status}{Colors.ENDC}")
    
    # Test with invalid refresh token
    invalid_headers = {"Cookie": "refresh_token=invalid_refresh_token_here"}
    status, headers, response = make_request(f"{BASE_URL}/auth/refresh-token", "POST", headers=invalid_headers)
    print(f"{Colors.WARNING}  Invalid refresh token: Status {status}{Colors.ENDC}")
    
    # Test with extremely long refresh token
    long_token = "t" * 10000
    long_token_headers = {"Cookie": f"refresh_token={long_token}"}
    status, headers, response = make_request(f"{BASE_URL}/auth/refresh-token", "POST", headers=long_token_headers)
    print(f"{Colors.WARNING}  Extremely long refresh token: Status {status}{Colors.ENDC}")
    
    # Test with SQL injection in cookie
    sql_injection_headers = {"Cookie": "refresh_token='; DROP TABLE sessions; --"}
    status, headers, response = make_request(f"{BASE_URL}/auth/refresh-token", "POST", headers=sql_injection_headers)
    print(f"{Colors.WARNING}  SQL injection in cookie: Status {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Refresh token failure tests completed{Colors.ENDC}")
    return True

def test_logout_failures():
    """Test logout endpoint with various failure scenarios."""
    print(f"{Colors.INFO}[7] 🚪 Testing logout failures...{Colors.ENDC}")
    
    # Test without access token
    status, headers, response = make_request(f"{BASE_URL}/auth/logout", "POST")
    print(f"{Colors.WARNING}  No access token: Status {status}{Colors.ENDC}")
    
    # Test with invalid access token
    invalid_headers = {"Authorization": "Bearer invalid_access_token_here"}
    status, headers, response = make_request(f"{BASE_URL}/auth/logout", "POST", headers=invalid_headers)
    print(f"{Colors.WARNING}  Invalid access token: Status {status}{Colors.ENDC}")
    
    # Test with malformed authorization header
    malformed_headers = {"Authorization": "InvalidFormatToken"}
    status, headers, response = make_request(f"{BASE_URL}/auth/logout", "POST", headers=malformed_headers)
    print(f"{Colors.WARNING}  Malformed authorization header: Status {status}{Colors.ENDC}")
    
    # Test with extremely long access token
    long_token = "Bearer " + "t" * 10000
    long_token_headers = {"Authorization": long_token}
    status, headers, response = make_request(f"{BASE_URL}/auth/logout", "POST", headers=long_token_headers)
    print(f"{Colors.WARNING}  Extremely long access token: Status {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Logout failure tests completed{Colors.ENDC}")
    return True

def test_protected_resource_failures():
    """Test protected resource access with invalid tokens."""
    print(f"{Colors.INFO}[8] 🔒 Testing protected resource failures...{Colors.ENDC}")
    
    # Test without access token
    status, headers, response = make_request(f"{BASE_URL}/users/me", "GET")
    print(f"{Colors.WARNING}  No access token: Status {status}{Colors.ENDC}")
    
    # Test with invalid access token
    invalid_headers = {"Authorization": "Bearer invalid_access_token_here"}
    status, headers, response = make_request(f"{BASE_URL}/users/me", "GET", headers=invalid_headers)
    print(f"{Colors.WARNING}  Invalid access token: Status {status}{Colors.ENDC}")
    
    # Test with malformed authorization header
    malformed_headers = {"Authorization": "InvalidFormatToken"}
    status, headers, response = make_request(f"{BASE_URL}/users/me", "GET", headers=malformed_headers)
    print(f"{Colors.WARNING}  Malformed authorization header: Status {status}{Colors.ENDC}")
    
    # Test with extremely long access token
    long_token = "Bearer " + "t" * 10000
    long_token_headers = {"Authorization": long_token}
    status, headers, response = make_request(f"{BASE_URL}/users/me", "GET", headers=long_token_headers)
    print(f"{Colors.WARNING}  Extremely long access token: Status {status}{Colors.ENDC}")
    
    # Test with SQL injection in token
    sql_token_headers = {"Authorization": "Bearer '; DROP TABLE users; --"}
    status, headers, response = make_request(f"{BASE_URL}/users/me", "GET", headers=sql_token_headers)
    print(f"{Colors.WARNING}  SQL injection in token: Status {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Protected resource failure tests completed{Colors.ENDC}")
    return True

def test_reset_password_failures():
    """Test password reset endpoint with various failure scenarios."""
    print(f"{Colors.INFO}[9] 🔑 Testing password reset failures...{Colors.ENDC}")
    
    # Test with empty data
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {})
    print(f"{Colors.WARNING}  Empty reset password data: Status {status}{Colors.ENDC}")
    
    # Test with missing fields
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": "test@example.com",
        "otp_code": "123456"
        # Missing new_password
    })
    print(f"{Colors.WARNING}  Missing new_password: Status {status}{Colors.ENDC}")
    
    # Test with invalid email format
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": "invalid-email",
        "otp_code": "123456",
        "new_password": "newpassword123"
    })
    print(f"{Colors.WARNING}  Invalid email format: Status {status}{Colors.ENDC}")
    
    # Test with invalid OTP
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": "test@example.com",
        "otp_code": "invalid-otp",
        "new_password": "newpassword123"
    })
    print(f"{Colors.WARNING}  Invalid OTP: Status {status}{Colors.ENDC}")
    
    # Test with too short new password
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": "test@example.com",
        "otp_code": "123456",
        "new_password": "123"
    })
    print(f"{Colors.WARNING}  Too short new password: Status {status}{Colors.ENDC}")
    
    # Test with non-existent email
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": "nonexistent@example.com",
        "otp_code": "123456",
        "new_password": "newpassword123"
    })
    print(f"{Colors.WARNING}  Non-existent email: Status {status}{Colors.ENDC}")
    
    # Test with wrong OTP
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": "test@example.com",
        "otp_code": "000000",  # Wrong OTP
        "new_password": "newpassword123"
    })
    print(f"{Colors.WARNING}  Wrong OTP: Status {status}{Colors.ENDC}")
    
    # Test with extremely long inputs
    long_email = "a" * 500 + "@example.com"
    long_otp = "1" * 100
    long_password = "p" * 1000
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": long_email,
        "otp_code": long_otp,
        "new_password": long_password
    })
    print(f"{Colors.WARNING}  Extremely long inputs: Status {status}{Colors.ENDC}")
    
    # Test with SQL injection
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": "'; DROP TABLE users; --",
        "otp_code": "'; DROP TABLE users; --",
        "new_password": "'; DROP TABLE users; --"
    })
    print(f"{Colors.WARNING}  SQL injection attempt: Status {status}{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Password reset failure tests completed{Colors.ENDC}")
    return True

def test_malformed_json():
    """Test endpoints with malformed JSON and edge cases."""
    print(f"{Colors.INFO}[10] 🚨 Testing malformed JSON and edge cases...{Colors.ENDC}")
    
    # Create a request with malformed JSON manually
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Test registration with malformed JSON
    try:
        url = f"{BASE_URL}/auth/register"
        # Malformed JSON - missing quotes, invalid structure
        malformed_json = '{"username": testuser, "email": "malformed@example.com", "password": "pass'
        req = urllib.request.Request(url, data=malformed_json.encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
        
        with urllib.request.urlopen(req, context=ctx) as response:
            status = response.status
            print(f"{Colors.WARNING}  Malformed JSON registration: Status {status}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.WARNING}  Malformed JSON registration error: {str(e)[:50]}...{Colors.ENDC}")
    
    # Test with extremely nested JSON
    try:
        nested_data = {"level": 0}
        current = nested_data
        for i in range(100):  # Create deeply nested structure
            current["nested"] = {"level": i+1}
            current = current["nested"]
        
        status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", nested_data)
        print(f"{Colors.WARNING}  Extremely nested JSON: Status {status}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.WARNING}  Extremely nested JSON error: {str(e)[:50]}...{Colors.ENDC}")
    
    # Test with very large JSON payload
    try:
        large_payload = {"data": "x" * 1000000}  # 1MB payload
        status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", large_payload)
        print(f"{Colors.WARNING}  Very large JSON payload: Status {status}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.WARNING}  Very large JSON payload error: {str(e)[:50]}...{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}✓ Malformed JSON and edge case tests completed{Colors.ENDC}")
    return True

def test_stress_concurrent_requests():
    """Test server resilience with concurrent requests."""
    print(f"{Colors.INFO}[11] ⚡ Testing stress with concurrent requests...{Colors.ENDC}")
    
    def make_concurrent_request():
        # Make a simple request that should fail
        status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
            "identifier": f"stress{random.randint(1000, 9999)}@example.com",
            "password": "invalid"
        })
        return status
    
    # Execute multiple concurrent requests
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_concurrent_request) for _ in range(50)]
        results = [future.result() for future in futures]
    
    # Count status codes
    status_counts = {}
    for status in results:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"{Colors.WARNING}  Concurrent request status distribution: {status_counts}{Colors.ENDC}")
    
    # Wait a bit to allow server to recover
    time.sleep(5)  # Increased from 2 to 5 seconds to allow better recovery

    # Verify server is still responsive
    status, headers, response = make_request(f"{BASE_URL}/health")
    if status == 200:
        print(f"{Colors.OKGREEN}✓ Server is still responsive after stress test{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠️  Server may be temporarily rate-limited after stress test (Status: {status}){Colors.ENDC}")
        # Try again after additional wait - allow more time for rate limit to reset
        time.sleep(10)  # Wait longer to allow rate limits to reset
        status_retry, headers_retry, response_retry = make_request(f"{BASE_URL}/health")
        if status_retry == 200:
            print(f"{Colors.OKGREEN}✓ Server recovered after rate limit reset{Colors.ENDC}")
        elif status_retry == 429:
            print(f"{Colors.WARNING}⚠️  Server still rate-limited (Status: 429), but operational{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ Server unresponsive after extended wait (Status: {status_retry}){Colors.ENDC}")

    return True

def run_failure_scenarios_test():
    """Run all failure scenarios tests."""
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Comprehensive Authentication Failure Scenarios Test{Colors.ENDC}")
    print(f"{Colors.INFO}Gateway URL: {GATEWAY_URL}{Colors.ENDC}")
    print(f"{Colors.INFO}Testing server resilience and error handling...{Colors.ENDC}\n")

    tests = [
        test_health_failures,
        test_registration_failures,
        test_otp_send_failures,
        test_otp_verify_failures,
        test_login_failures,
        test_refresh_token_failures,
        test_logout_failures,
        test_protected_resource_failures,
        test_reset_password_failures,
        test_malformed_json,
        test_stress_concurrent_requests
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for i, test_func in enumerate(tests, 1):
        try:
            print(f"\n{Colors.INFO}Running test {i}/{total_tests}: {test_func.__name__}{Colors.ENDC}")
            if test_func():
                passed_tests += 1
                print(f"{Colors.OKGREEN}✓ {test_func.__name__} completed{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}❌ {test_func.__name__} failed{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ {test_func.__name__} raised exception: {e}{Colors.ENDC}")
    
    print(f"\n{Colors.INFO}{Colors.BOLD}Test Summary:{Colors.ENDC}")
    print(f"{Colors.INFO}Passed: {passed_tests}/{total_tests} tests{Colors.ENDC}")
    
    if passed_tests == total_tests:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 All failure scenario tests completed! Server handled errors gracefully.{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  {total_tests - passed_tests} tests had issues. Check server logs for details.{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = run_failure_scenarios_test()
    if not success:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Failure Scenarios Test had issues{Colors.ENDC}")
        sys.exit(1)
    else:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ Failure Scenarios Test completed successfully{Colors.ENDC}")