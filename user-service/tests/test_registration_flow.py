#!/usr/bin/env python3
"""
Script to test the account registration and verification flow.

Scenario:
1. Register a new user (which creates an inactive account).
2. Request an OTP for the 'register' action.
3. Extract OTP from the response (requires DEBUG mode).
4. Call the verification endpoint (/auth/register/verify).
5. Attempt to log in to confirm the account is now active.
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
    print(f"{Colors.HEADER}🧪 Testing Registration & Verification Flow{Colors.ENDC}")
    
    # 1. Setup User
    rnd = random.randint(1000, 9999)
    email = f"reg_verify_test_{rnd}@example.com"
    password = "password123"
    username = f"reg_verify_{rnd}"
    
    print(f"\n[1] Registering new user: {email}")
    status, reg_res = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": username, "email": email, "password": password,
        "first_name": "Reg", "last_name": "Verify"
    })

    if status != 201:
        print(f"{Colors.FAIL}❌ Registration failed: {reg_res}{Colors.ENDC}")
        return
    
    user_id = reg_res['data']['id']
    print(f"{Colors.INFO}    User created (ID: {user_id}). Status: Inactive.{Colors.ENDC}")

    # 2. Request OTP for registration
    print(f"\n[2] Requesting OTP for 'register' action...")
    status, otp_res = make_request(f"{BASE_URL}/auth/otp/send", "POST", {
        "email": email, "action": "register"
    })
    
    if status != 200:
        print(f"{Colors.FAIL}❌ OTP Request failed: {otp_res}{Colors.ENDC}")
        return

    # Safe data extraction
    otp_data = otp_res.get('data')
    reg_otp = otp_data.get('otp_code') if otp_data else None

    if not reg_otp:
        print(f"{Colors.FAIL}❌ OTP not found in response. Ensure DEBUG=True is set on the server.{Colors.ENDC}")
        return
    
    print(f"{Colors.OKGREEN}✓ OTP Received: {reg_otp}{Colors.ENDC}")

    # 3. Verify account with OTP
    print(f"\n[3] Verifying account with endpoint /auth/register/verify...")
    status, verify_res = make_request(f"{BASE_URL}/auth/register/verify", "POST", {
        "email": email,
        "otp_code": reg_otp
    })

    if status == 200:
        print(f"{Colors.OKGREEN}✓ Account verification successful.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Account verification failed: {verify_res}{Colors.ENDC}")
        return

    # 4. Attempt login to confirm activation
    print(f"\n[4] Attempting to log in...")
    status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", {
        "identifier": email, "password": password
    })

    if status == 200:
        print(f"{Colors.OKGREEN}🎉 SUCCESS! Login successful, account is active.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Failed to log in after verification.{Colors.ENDC}")
        print(json.dumps(login_res, indent=2))

if __name__ == "__main__":
    run_test()
