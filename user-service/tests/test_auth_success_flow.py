#!/usr/bin/env python3
"""
Comprehensive End-to-End Authentication Flow Test Script

This script tests the complete authentication flow through the API Gateway,
including registration, verification, login, refresh, logout, and password reset.

Scenario:
1. Health check to verify services are running
2. Register a new user
3. Request OTP for registration
4. Verify the registration with OTP
5. Login with credentials
6. Access protected resource (users endpoint) with access token
7. Simulate access token expiration and refresh token
8. Access protected resource again with new access token
9. Logout from the system
10. Password reset flow: request OTP for reset, reset password, login with new password

Usage:
    python3 user-service/tests/test_auth_success_flow.py
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

def run_auth_flow_test():
    """Run the complete end-to-end authentication flow test."""
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Comprehensive End-to-End Authentication Flow Test{Colors.ENDC}")
    print(f"{Colors.INFO}Gateway URL: {GATEWAY_URL}{Colors.ENDC}")
    
    # Generate random values for this test run
    rnd = random.randint(10000, 99999)
    email = f"e2e_test_user_{rnd}@example.com"
    username = f"e2e_user_{rnd}"
    password = "SecurePassword123!"
    new_password = "NewSecurePassword456!"
    
    print(f"{Colors.INFO}Test User: {email}{Colors.ENDC}\n")
    
    # Track tokens and cookies throughout the flow
    access_token = None
    refresh_token = None
    
    # 1. Health Check
    print(f"{Colors.INFO}[1] 🔍 Health Check - Verifying services are running...{Colors.ENDC}")
    status, headers, response = make_request(f"{BASE_URL}/health")

    if status == 200 and response.get('status') in ['healthy', 'RUNNING']:
        print(f"{Colors.OKGREEN}✓ Health check passed - Services are running{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Health check failed: {response}{Colors.ENDC}")
        return False
    
    # 2. Registration
    print(f"\n{Colors.INFO}[2] 📝 Registering new user: {email}{Colors.ENDC}")
    status, headers, response = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": username, 
        "email": email, 
        "password": password,
        "first_name": "E2E", 
        "last_name": "Tester"
    })

    if status == 201:
        user_id = response.get('data', {}).get('id')
        print(f"{Colors.OKGREEN}✓ Registration successful (User ID: {user_id}){Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Registration failed: {response}{Colors.ENDC}")
        return False
    
    # 3. Request OTP for registration
    print(f"\n{Colors.INFO}[3] 📧 Requesting OTP for registration verification...{Colors.ENDC}")
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": email, 
        "action": "register"
    })

    if status == 200:
        otp_data = response.get('data')
        reg_otp = otp_data.get('otp_code') if otp_data else None
        
        if reg_otp:
            print(f"{Colors.OKGREEN}✓ OTP received: {reg_otp}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ OTP not found in response. Ensure DEBUG=True is set on the server.{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}❌ OTP request failed: {response}{Colors.ENDC}")
        return False

    # 4. Verify registration with OTP
    print(f"\n{Colors.INFO}[4] ✅ Verifying account with OTP...{Colors.ENDC}")
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/verify", "POST", {
        "email": email,
        "otp_code": reg_otp
    })

    if status == 200:
        print(f"{Colors.OKGREEN}✓ Account verification successful{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Account verification failed: {response}{Colors.ENDC}")
        return False

    # 5. Login with credentials
    print(f"\n{Colors.INFO}[5] 🔐 Logging in with registered credentials...{Colors.ENDC}")
    status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": email, 
        "password": password
    })

    if status == 200:
        access_token = response.get('data', {}).get('access_token')
        refresh_token = get_cookie_value(headers, "refresh_token")
        
        if access_token and refresh_token:
            print(f"{Colors.OKGREEN}✓ Login successful{Colors.ENDC}")
            print(f"{Colors.INFO}  Access Token Length: {len(access_token)}{Colors.ENDC}")
            print(f"{Colors.INFO}  Refresh Token Length: {len(refresh_token)}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}❌ Missing tokens in login response{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}❌ Login failed: {response}{Colors.ENDC}")
        return False

    # 6. Access protected resource with access token
    print(f"\n{Colors.INFO}[6] 🔒 Accessing protected resource (/users/me endpoint)...{Colors.ENDC}")
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    status, headers, response = make_request(f"{BASE_URL}/users/me", "GET", headers=auth_headers)

    if status == 200:
        print(f"{Colors.OKGREEN}✓ Successfully accessed protected resource{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Failed to access protected resource: {response}{Colors.ENDC}")
        return False

    # 7. Simulate access token expiration and refresh token
    print(f"\n{Colors.INFO}[7] ♻️  Refreshing access token using refresh token...{Colors.ENDC}")
    refresh_headers = {"Cookie": f"refresh_token={refresh_token}"}
    status, headers, response = make_request(f"{BASE_URL}/auth/refresh-token", "POST", headers=refresh_headers)

    if status == 200:
        new_access_token = response.get('data', {}).get('access_token')
        new_refresh_token = get_cookie_value(headers, "refresh_token")

        if new_access_token and new_refresh_token:
            print(f"{Colors.OKGREEN}✓ Token refresh successful{Colors.ENDC}")
            print(f"{Colors.INFO}  New Access Token Length: {len(new_access_token)}{Colors.ENDC}")
            print(f"{Colors.INFO}  New Refresh Token Length: {len(new_refresh_token)}{Colors.ENDC}")

            # Update tokens for subsequent requests
            access_token = new_access_token
            refresh_token = new_refresh_token
        else:
            print(f"{Colors.FAIL}❌ Missing tokens in refresh response{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}❌ Token refresh failed: {response}{Colors.ENDC}")
        return False

    # 8. Access protected resource again with new access token
    print(f"\n{Colors.INFO}[8] 🔒 Accessing protected resource with new access token...{Colors.ENDC}")
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    status, headers, response = make_request(f"{BASE_URL}/users/me", "GET", headers=auth_headers)

    if status == 200:
        print(f"{Colors.OKGREEN}✓ Successfully accessed protected resource with new token{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Failed to access protected resource with new token: {response}{Colors.ENDC}")
        return False

    # 9. Logout from the system
    print(f"\n{Colors.INFO}[9] 🚪 Logging out from the system...{Colors.ENDC}")
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    status, headers, response = make_request(f"{BASE_URL}/auth/logout", "POST", headers=auth_headers)

    if status == 200:
        print(f"{Colors.OKGREEN}✓ Logout successful{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠️  Logout response: {response}{Colors.ENDC}")

    # 10. Password reset flow
    print(f"\n{Colors.INFO}[10] 🔑 Testing password reset flow...{Colors.ENDC}")
    
    # 10a. Request OTP for password reset
    print(f"{Colors.INFO}  [10a] 📧 Requesting OTP for password reset...{Colors.ENDC}")
    status, headers, response = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": email, 
        "action": "reset_password"
    })

    if status == 200:
        otp_data = response.get('data')
        reset_otp = otp_data.get('otp_code') if otp_data else None
        
        if reset_otp:
            print(f"{Colors.OKGREEN}  ✓ Password reset OTP received: {reset_otp}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}  ❌ Password reset OTP not found in response{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}  ❌ Password reset OTP request failed: {response}{Colors.ENDC}")
        return False

    # 10b. Reset password using OTP
    print(f"{Colors.INFO}  [10b] 🔄 Resetting password with OTP...{Colors.ENDC}")
    status, headers, response = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": email,
        "otp_code": reset_otp,
        "new_password": new_password
    })

    if status == 200:
        print(f"{Colors.OKGREEN}  ✓ Password reset successful{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}  ❌ Password reset failed: {response}{Colors.ENDC}")
        return False

    # 10c. Login with new password
    print(f"{Colors.INFO}  [10c] 🔐 Logging in with new password...{Colors.ENDC}")
    status, headers, response = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": email, 
        "password": new_password
    })

    if status == 200:
        access_token = response.get('data', {}).get('access_token')
        refresh_token = get_cookie_value(headers, "refresh_token")
        
        if access_token and refresh_token:
            print(f"{Colors.OKGREEN}  ✓ Login with new password successful{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}  ❌ Missing tokens in login response{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.FAIL}  ❌ Login with new password failed: {response}{Colors.ENDC}")
        return False

    # 11. Final verification - access protected resource with new credentials
    print(f"\n{Colors.INFO}[11] ✅ Final verification - accessing protected resource...{Colors.ENDC}")
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    status, headers, response = make_request(f"{BASE_URL}/users/me", "GET", headers=auth_headers)

    if status == 200:
        print(f"{Colors.OKGREEN}✓ Final verification successful - All authentication flows working correctly{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Final verification failed: {response}{Colors.ENDC}")
        return False

    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 SUCCESS! All authentication flows completed successfully!{Colors.ENDC}")
    print(f"{Colors.INFO}Tested endpoints: register, login, refresh, logout, otp, reset-password, protected resources{Colors.ENDC}")
    
    return True

if __name__ == "__main__":
    success = run_auth_flow_test()
    if not success:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ End-to-End Authentication Flow Test FAILED{Colors.ENDC}")
        sys.exit(1)
    else:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ End-to-End Authentication Flow Test PASSED{Colors.ENDC}")