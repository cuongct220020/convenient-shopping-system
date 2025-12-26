#!/usr/bin/env python3
"""
Script to test the "Forgot Password" Flow.

Scenario:
1. Setup: Login as Admin.
2. Register a new user (Status: Inactive).
3. Activate the new user using Admin Token (Simulating OTP Verification).
4. Login with Old Password (Simulating normal usage).
5. Logout (User forgets password).
6. Request Password Reset OTP.
7. Reset Password using the OTP.
8. Verify login with the NEW password.

Usage:
    python3 user-service/scripts/test_reset_password_flow_v2.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import random

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
        print(f"{Colors.FAIL}Connection Error: {e}{Colors.ENDC}")
        sys.exit(1)

def run_test():
    print(f"{Colors.HEADER}🧪 Testing Forgot Password Flow{Colors.ENDC}")
    
    # 0. Login as Admin (Setup)
    print(f"\n[0] Logging in as Admin ({ADMIN_USERNAME})...")
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Admin Login failed.{Colors.ENDC}")
        return

    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"{Colors.OKGREEN}✓ Admin setup complete.{Colors.ENDC}")

    # 1. Setup User
    rnd = random.randint(1000, 9999)
    email = f"reset_test_{rnd}@example.com"
    username = f"reset_user_{rnd}"
    old_password = "OldPassword123!"
    new_password = "NewPassword456!"
    
    print(f"\n[1] Registering user: {email}")
    status, reg_res = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": username, "email": email, "password": old_password,
        "first_name": "Reset", "last_name": "Tester"
    })
    
    if status != 201:
        print(f"{Colors.FAIL}❌ Registration failed.{Colors.ENDC}")
        return
    
    user_id = reg_res['data']['id']
    print(f"{Colors.INFO}    User created (ID: {user_id}).{Colors.ENDC}")

    # 2. Activate User via Admin API (Simulating Registration OTP Verification)
    print(f"\n[2] Activating User (Simulating OTP Verification)...")
    status, active_res = make_request(
        f"{BASE_URL}/admin/users/{user_id}", 
        "PATCH", 
        {"is_active": True}, 
        admin_headers
    )
    if status == 200:
        print(f"{Colors.OKGREEN}✓ User activated.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Activation failed.{Colors.ENDC}")
        return

    # 3. Login with Old Password
    print(f"\n[3] Logging in with OLD password...")
    status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": email, "password": old_password
    })
    
    if status == 200:
        user_token = login_res['data']['access_token']
        print(f"{Colors.OKGREEN}✓ Login successful.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Login failed.{Colors.ENDC}")
        return

    # 4. Logout
    print(f"\n[4] Logging out (Simulating session end)...")
    headers = {"Authorization": f"Bearer {user_token}"}
    status, logout_res = make_request(f"{BASE_URL}/auth/logout", "POST", headers=headers)
    if status == 200:
        print(f"{Colors.OKGREEN}✓ Logout successful.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}⚠️ Logout warning: {logout_res}{Colors.ENDC}")

    # 5. Forgot Password -> Request OTP
    print(f"\n[5] Requesting Password Reset OTP (Forgot Password)...")
    status, req_res = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": email, "action": "reset_password"
    })
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Request failed: {req_res}{Colors.ENDC}")
        return

    # Safe data extraction
    req_data = req_res.get('data')
    otp_code = req_data.get('otp_code') if req_data else None

    if not otp_code:
        print(f"{Colors.FAIL}❌ OTP not found. Ensure DEBUG=True{Colors.ENDC}")
        return
        
    print(f"{Colors.OKGREEN}✓ OTP Received: {otp_code}{Colors.ENDC}")

    # 6. Reset Password with OTP
    print(f"\n[6] Resetting Password with OTP...")
    status, reset_res = make_request(f"{BASE_URL}/auth/reset-password", "POST", {
        "email": email,
        "new_password": new_password,
        "otp_code": otp_code
    })

    if status == 200:
        print(f"{Colors.OKGREEN}✓ Password reset successful.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Reset failed: {reset_res}{Colors.ENDC}")
        return

    # 7. Verify Login with New Password
    print(f"\n[7] Verifying login with NEW password...")
    status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": email, "password": new_password
    })

    if status == 200:
        print(f"{Colors.OKGREEN}🎉 SUCCESS! Logged in with new password.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Failed to login with new password.{Colors.ENDC}")

if __name__ == "__main__":
    run_test()