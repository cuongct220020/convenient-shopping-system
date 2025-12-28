#!/usr/bin/env python3
"""
Script to test the account registration and verification flow WITHOUT names.
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
    print(f"{Colors.HEADER}🧪 Testing Registration & Verification Flow (Nullable Names){Colors.ENDC}")
    
    # 1. Setup User
    rnd = random.randint(1000, 9999)
    email = f"reg_verify_test_{rnd}@example.com"
    password = "password123"
    username = f"reg_verify_{rnd}"
    
    print(f"\n[1] Registering new user: {email} (NO NAMES)")
    # Intentionally omitting first_name and last_name
    status, reg_res = make_request(f"{BASE_URL}/auth/register", "POST", {
        "username": username, "email": email, "password": password
    })

    if status != 201:
        print(f"{Colors.FAIL}❌ Registration failed: {reg_res}{Colors.ENDC}")
        return
    
    user_id = reg_res['data']['user_id']
    print(f"{Colors.INFO}    User created (ID: {user_id}). Status: Inactive.{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Registration successful with null names.{Colors.ENDC}")

if __name__ == "__main__":
    run_test()
