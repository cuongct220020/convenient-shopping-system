#!/usr/bin/env python3
"""
Authorization Failure Test Script for /me Endpoints in the user-service.

This script specifically tests authorization failures where users attempt to:
1. Access endpoints that don't belong to them (shouldn't be possible with /me endpoints but testing general principle)
2. Perform actions without proper permissions
3. Exploit potential authorization bypasses

Usage:
    python3 user-service/tests/test_me_management_authz_failures.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import time
import random

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

def register_test_user(suffix=""):
    """Register a test user and return credentials."""
    test_username = f"testuser_{int(time.time())}_{random.randint(1000, 9999)}{suffix}"
    test_email = f"test_{int(time.time())}_{random.randint(1000, 9999)}{suffix}@example.com"
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
        print_status(f"Test User Registration {suffix}", "SUCCESS", f"User: {test_email}")
        return test_email, test_password
    else:
        print_status(f"Test User Registration {suffix}", "FAILED", f"Status: {response['status_code']}")
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

def test_cross_user_access_attempts():
    """Test attempts to access other users' data through /me endpoints (should not be possible but testing for vulnerabilities)."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Cross-User Access Attempts{Colors.ENDC}")
    print("=" * 60)

    # Register two different users
    user1_email, user1_password = register_test_user("_user1")
    user2_email, user2_password = register_test_user("_user2")
    
    if not user1_email or not user2_email:
        print_status("Setup", "FAILED", "Could not register test users")
        return

    # Login as user1
    user1_token = login_user(user1_email, user1_password)
    user2_token = login_user(user2_email, user2_password)
    
    if not user1_token or not user2_token:
        print_status("Setup", "FAILED", "Could not login test users")
        return

    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # Test that user1 can access their own data
    print(f"\n{Colors.INFO}Verifying user1 can access their own data{Colors.ENDC}")
    response = make_request(f"{BASE_URL}/users/me/", method="GET", headers=user1_headers)
    if response["status_code"] == 200:
        user1_id = response["data"]["data"]["id"]
        print_status("User1 Self-Access", "SUCCESS", f"User1 ID: {user1_id}")
    else:
        print_status("User1 Self-Access", "FAILED", f"Could not access own data: {response['status_code']}")
        return

    # Test that user2 can access their own data
    print(f"\n{Colors.INFO}Verifying user2 can access their own data{Colors.ENDC}")
    response = make_request(f"{BASE_URL}/users/me/", method="GET", headers=user2_headers)
    if response["status_code"] == 200:
        user2_id = response["data"]["data"]["id"]
        print_status("User2 Self-Access", "SUCCESS", f"User2 ID: {user2_id}")
    else:
        print_status("User2 Self-Access", "FAILED", f"Could not access own data: {response['status_code']}")
        return

    # The /me endpoints should only allow access to the authenticated user's own data
    # So we can't really test cross-user access through /me endpoints directly
    # But we can test if there are any endpoints that might be vulnerable to ID manipulation
    print(f"\n{Colors.INFO}Testing that /me endpoints only return authenticated user's data{Colors.ENDC}")
    print_status("Cross-User Access", "INFO", "The /me endpoints by design should only return data for the authenticated user")

def test_permission_level_failures():
    """Test failures related to different permission levels."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Permission Level Failures{Colors.ENDC}")
    print("=" * 60)

    # Register a regular user
    user_email, user_password = register_test_user("_perm")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test attempts to access admin-only endpoints with regular user token
    admin_endpoints = [
        ("GET", "/admin/users"),
        ("GET", "/admin/users/1"),
        ("PUT", "/admin/users/1"),
        ("DELETE", "/admin/users/1"),
        ("GET", "/admin/groups"),
        ("POST", "/admin/groups"),
    ]

    for method, endpoint in admin_endpoints:
        print(f"\n{Colors.INFO}Testing {method} {endpoint} with regular user token{Colors.ENDC}")
        response = make_request(f"{BASE_URL}{endpoint}", method=method, headers=auth_headers, data={})
        
        if response["status_code"] in [401, 403]:
            print_status(f"{method} {endpoint}", "SUCCESS", f"Properly rejected (Status: {response['status_code']})")
        else:
            print_status(f"{method} {endpoint}", "FAILED", f"Should return 401/403, got {response['status_code']} - possible privilege escalation vulnerability!")

def test_token_manipulation_attempts():
    """Test attempts to manipulate tokens to gain unauthorized access."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Token Manipulation Attempts{Colors.ENDC}")
    print("=" * 60)

    # Register a user
    user_email, user_password = register_test_user("_token")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    # Test with token that has modified payload (but invalid signature)
    # This is hard to generate without the private key, so we'll test with obviously invalid tokens
    manipulated_tokens = [
        f"Bearer {access_token[:-10]}XXXXX",  # Corrupted token
        f"Bearer {access_token[:50]}{access_token[50:].replace('a', 'X')}",  # Modified token
    ]

    endpoints_to_test = [
        ("GET", "/users/me/"),
        ("GET", "/users/me/profile/identity"),
        ("GET", "/users/me/profile/health"),
    ]

    for token in manipulated_tokens:
        headers = {"Authorization": token}
        for method, endpoint in endpoints_to_test:
            print(f"\n{Colors.INFO}Testing {method} {endpoint} with manipulated token{Colors.ENDC}")
            response = make_request(f"{BASE_URL}{endpoint}", method=method, headers=headers, data={})
            
            if response["status_code"] in [401, 403]:
                print_status(f"Manipulated token access", "SUCCESS", f"{method} {endpoint} properly rejected (Status: {response['status_code']})")
            else:
                print_status(f"Manipulated token access", "CRITICAL", f"{method} {endpoint} should reject invalid token, got {response['status_code']} - potential security vulnerability!")

def test_session_fixation_attempts():
    """Test for potential session fixation vulnerabilities."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Session Fixation Attempts{Colors.ENDC}")
    print("=" * 60)

    # Register a user
    user_email, user_password = register_test_user("_session")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    # Login to get a valid token
    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test if old tokens are properly invalidated after password change
    print(f"\n{Colors.INFO}Testing if tokens are invalidated after password change{Colors.ENDC}")
    
    # Change password
    password_change_data = {
        "current_password": user_password,
        "new_password": "NewSecurePassword456!"
    }

    response = make_request(
        f"{BASE_URL}/users/me/change-password",
        method="POST",
        headers=auth_headers,
        data=password_change_data
    )

    if response["status_code"] == 200:
        print_status("Password Change", "SUCCESS", "Password changed successfully")
        
        # Try to access protected endpoint with old token (should fail)
        response = make_request(
            f"{BASE_URL}/users/me/",
            method="GET",
            headers=auth_headers  # Using old token
        )

        if response["status_code"] in [401, 403]:
            print_status("Old Token After Password Change", "SUCCESS", f"Old token properly invalidated (Status: {response['status_code']})")
        else:
            print_status("Old Token After Password Change", "CRITICAL", f"Old token still valid after password change (Status: {response['status_code']}) - session fixation vulnerability!")
    else:
        print_status("Password Change", "FAILED", f"Could not change password: {response['status_code']}")

def test_privilege_escalation_attempts():
    """Test for potential privilege escalation vulnerabilities."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Privilege Escalation Attempts{Colors.ENDC}")
    print("=" * 60)

    # Register a regular user
    user_email, user_password = register_test_user("_priv")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test if a regular user can somehow escalate to admin by manipulating requests
    # This would typically involve trying to set admin-level fields in profile updates
    escalation_attempts = [
        {"system_role": "admin"},  # Try to set role to admin
        {"is_admin": True},  # Try to set admin flag
        {"permissions": ["admin", "superuser"]},  # Try to set admin permissions
        {"role": "administrator"},  # Try to set role to administrator
    ]

    profile_endpoints = [
        "/users/me",
        "/users/me/profile/identity",
        "/users/me/profile/health",
    ]

    for escalation_data in escalation_attempts:
        for endpoint in profile_endpoints:
            print(f"\n{Colors.INFO}Testing privilege escalation via {endpoint} with data: {escalation_data}{Colors.ENDC}")
            response = make_request(
                f"{BASE_URL}{endpoint}",
                method="PATCH",
                headers=auth_headers,
                data=escalation_data
            )
            
            # Should either reject the request or ignore the privilege fields
            if response["status_code"] in [400, 422, 200]:
                if response["status_code"] == 200:
                    # Check if the privileged field was actually set
                    get_response = make_request(f"{BASE_URL}/users/me/", method="GET", headers=auth_headers)
                    if get_response["status_code"] == 200:
                        user_data = get_response["data"]["data"]
                        # Check if any of the escalation fields were set
                        escalation_successful = False
                        for field in escalation_data.keys():
                            if user_data.get(field) or any(priv in str(user_data.get('permissions', [])) for priv in ['admin', 'administrator']):
                                escalation_successful = True
                                break
                        
                        if escalation_successful:
                            print_status(f"Privilege escalation via {endpoint}", "CRITICAL", f"Potential privilege escalation vulnerability! Status: {response['status_code']}")
                        else:
                            print_status(f"Privilege escalation via {endpoint}", "SUCCESS", f"Request processed safely (Status: {response['status_code']})")
                else:
                    print_status(f"Privilege escalation via {endpoint}", "SUCCESS", f"Request properly rejected (Status: {response['status_code']})")
            else:
                print_status(f"Privilege escalation via {endpoint}", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def test_rate_limit_bypass_attempts():
    """Test attempts to bypass rate limiting."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing Rate Limit Bypass Attempts{Colors.ENDC}")
    print("=" * 60)

    # Register a user
    user_email, user_password = register_test_user("_rate")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test multiple rapid requests to see if rate limiting is properly enforced
    print(f"\n{Colors.INFO}Testing rapid requests to /users/me/ endpoint{Colors.ENDC}")
    
    import time
    from concurrent.futures import ThreadPoolExecutor
    
    def make_request_func():
        response = make_request(f"{BASE_URL}/users/me/", method="GET", headers=auth_headers)
        return response["status_code"]
    
    # Send many requests quickly
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request_func) for _ in range(30)]
        results = [future.result() for future in futures]
    end_time = time.time()
    
    status_counts = {}
    for status in results:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print_status("Rapid Requests", "INFO", f"Completed 30 requests in {end_time - start_time:.2f}s. Status distribution: {status_counts}")
    
    if 429 in status_counts:
        print_status("Rate Limiting", "SUCCESS", f"Rate limiting properly enforced ({status_counts[429]} 429 responses)")
    else:
        print_status("Rate Limiting", "INFO", "No rate limiting responses (429) detected - may not be implemented or threshold too high")

def run_authz_failure_tests():
    """Run all authorization failure tests."""
    print(f"{Colors.HEADER}{Colors.BOLD}🔒 Running /me Endpoints Authorization Failure Tests{Colors.ENDC}")
    print(f"{Colors.INFO}Testing authorization failures and permission-related vulnerabilities{Colors.ENDC}")
    
    test_cross_user_access_attempts()
    test_permission_level_failures()
    test_token_manipulation_attempts()
    test_session_fixation_attempts()
    test_privilege_escalation_attempts()
    test_rate_limit_bypass_attempts()
    
    print(f"\n{Colors.BOLD}🎉 Authorization Failure Testing Complete!{Colors.ENDC}")
    print(f"{Colors.INFO}Check for any CRITICAL issues above that indicate potential authorization vulnerabilities.{Colors.ENDC}")

if __name__ == "__main__":
    run_authz_failure_tests()