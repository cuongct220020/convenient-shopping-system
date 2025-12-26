#!/usr/bin/env python3
"""
Script to test the Change Email Flow.

Scenario:
1. Login as Admin to get Admin Token.
2. Register a new user (Status: Inactive).
3. Activate the new user using Admin Token (via Admin API).
4. Login as the new User.
5. Request to change email (Authenticated).
6. Extract OTP from Debug response.
7. Confirm email change with OTP.
8. Verify login works with the NEW email.

Usage:
    python3 user-service/scripts/test_change_email_flow.py
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
    print(f"{Colors.HEADER}🧪 Testing Change Email Flow (Admin Activation){Colors.ENDC}")
    
    # 0. Login as Admin
    print(f"\n[0] Logging in as Admin ({ADMIN_USERNAME})...")
    status, admin_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": ADMIN_USERNAME, "password": ADMIN_PASSWORD
    })
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Admin Login failed. Setup Admin user first!{Colors.ENDC}")
        return

    admin_token = admin_login['data']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"{Colors.OKGREEN}✓ Admin logged in.{Colors.ENDC}")

    # 1. Setup New User
    rnd = random.randint(10000, 99999)
    current_email = f"user_{rnd}@test.com"
    new_email = f"user_{rnd}_new@test.com"
    password = "password123"
    username = f"user_{rnd}"
    
    print(f"\n[1] Registering new user: {current_email}")
    status, reg_res = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": username, "email": current_email, "password": password,
        "first_name": "Test", "last_name": "User"
    })

    if status != 201:
        print(f"{Colors.FAIL}❌ Registration failed: {reg_res}{Colors.ENDC}")
        return

    # Extract User ID from registration response to activate
    user_id = reg_res['data']['id']
    print(f"{Colors.INFO}    User created (ID: {user_id}). Status: Inactive.{Colors.ENDC}")

    # 2. Activate User via Admin API
    print(f"\n[2] Activating User via Admin API...")
    status, active_res = make_request(
        f"{BASE_URL}/admin/users/{user_id}", 
        "PATCH", 
        {"is_active": True}, 
        admin_headers
    )

    if status != 200:
        print(f"{Colors.FAIL}❌ Admin Activation failed: {active_res}{Colors.ENDC}")
        return
    print(f"{Colors.OKGREEN}✓ User activated by Admin.{Colors.ENDC}")
    
    # 3. Login as User
    print(f"\n[3] Logging in as User...")
    status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": current_email, "password": password
    })
    
    if status != 200:
        print(f"{Colors.FAIL}❌ User Login failed.{Colors.ENDC}")
        print(json.dumps(login_res, indent=2))
        return

    user_token = login_res['data']['access_token']
    user_headers = {"Authorization": f"Bearer {user_token}"}
    print(f"{Colors.OKGREEN}✓ User Login successful.{Colors.ENDC}")

    # 4. Request Email Change
    print(f"\n[4] Requesting email change to: {new_email}")
    status, req_res = make_request(
        f"{BASE_URL}/users/me/email/request-change", 
        "POST", 
        {"new_email": new_email},
        user_headers
    )
    
    if status != 200:
        print(f"{Colors.FAIL}❌ Request failed: {req_res}{Colors.ENDC}")
        return

    req_data = req_res.get('data')
    otp_code = req_data.get('otp_code') if req_data else None

    if not otp_code:
        print(f"{Colors.FAIL}❌ OTP not found. Ensure DEBUG=True{Colors.ENDC}")
        return
        
    print(f"{Colors.OKGREEN}✓ OTP Sent. Retrieved OTP: {otp_code}{Colors.ENDC}")

    # 5. Confirm Email Change
    print(f"\n[5] Confirming email change...")
    status, conf_res = make_request(
        f"{BASE_URL}/users/me/email/confirm-change",
        "POST",
        {
            "new_email": new_email,
            "otp_code": otp_code
        },
        user_headers
    )

    if status == 200:
        print(f"{Colors.OKGREEN}✓ Confirmation successful.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Confirmation failed: {conf_res}{Colors.ENDC}")
        return

    # 6. Verify Login with NEW email
    print(f"\n[6] Verifying login with NEW email...")
    status, new_login = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": new_email, "password": password
    })

    if status == 200:
        print(f"{Colors.OKGREEN}🎉 SUCCESS! Logged in with new email.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Failed to login with new email.{Colors.ENDC}")

if __name__ == "__main__":
    run_test()