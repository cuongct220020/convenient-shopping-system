#!/usr/bin/env python3
"""
Script to test the login and logout flow for the admin user via Kong Gateway.

Usage:
    python3 user-service/scripts/test_login_logout_flow.py

Requirements:
    - User Service must be running.
    - Kong Gateway must be running at https://localhost:8000.
    - Admin user (admin/admin) must exist (run create_admin_user.py if not).
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
LOGIN_ENDPOINT = "/api/v1/user-service/auth/login"
LOGOUT_ENDPOINT = "/api/v1/user-service/auth/logout"
USERNAME = os.getenv("ADMIN_USERNAME", "admin")
PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

def make_request(url, method="GET", data=None, headers=None):
    """Helper function to make HTTP requests using standard library."""
    if headers is None:
        headers = {}
    
    # Allow self-signed certificates for localhost (common in dev environments)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    encoded_data = None
    if data:
        encoded_data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
        
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            response_body = response.read().decode('utf-8')
            try:
                json_body = json.loads(response_body)
            except json.JSONDecodeError:
                json_body = response_body
            return response.status, json_body
    except urllib.error.HTTPError as e:
        response_body = e.read().decode('utf-8')
        try:
            body_json = json.loads(response_body)
        except json.JSONDecodeError:
            body_json = {"raw": response_body}
        return e.code, body_json
    except urllib.error.URLError as e:
        print(f"❌ Connection Error to {url}: {e}")
        return 0, None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return 0, None

def main():
    print("=" * 60)
    print(f"🧪 Testing Login/Logout Flow via Kong Gateway")
    print(f"   URL: {GATEWAY_URL}")
    print(f"   User: {USERNAME}")
    print("=" * 60)
    
    # ---------------------------------------------------------
    # 1. Login
    # ---------------------------------------------------------
    print("\n1️⃣  Step 1: Attempting Login...")
    login_url = f"{GATEWAY_URL}{LOGIN_ENDPOINT}"
    login_payload = {
        "identifier": USERNAME,
        "password": PASSWORD
    }
    
    status, response = make_request(login_url, "POST", login_payload)
    
    if status == 0:
        print("   -> Could not connect to Gateway. Is it running?")
        sys.exit(1)
        
    if status != 200:
        print(f"   ❌ Login Failed! Status: {status}")
        print(f"   Response: {json.dumps(response, indent=2)}")
        print("\n   [Tip] If the user does not exist, run:")
        print("   python3 user-service/scripts/create_admin_user.py")
        sys.exit(1)
        
    print("   ✅ Login Successful!")
    
    # Extract Token
    # Expecting structure: { "status": "success", "data": { "access_token": "...", ... } }
    data = response.get('data', {})
    access_token = data.get('access_token')
    
    if not access_token:
        # Fallback check if token is at root level (unlikely based on code but safe)
        access_token = response.get('access_token')
    
    if not access_token:
        print("   ❌ Error: Could not find 'access_token' in response.")
        print(f"   Response structure: {json.dumps(response, indent=2)}")
        sys.exit(1)
        
    print(f"   🔑 Access Token received (len={len(access_token)})")
    
    # ---------------------------------------------------------
    # 2. Logout
    # ---------------------------------------------------------
    print("\n2️⃣  Step 2: Attempting Logout...")
    logout_url = f"{GATEWAY_URL}{LOGOUT_ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    status, response = make_request(logout_url, "POST", headers=headers)
    
    if status == 200:
        print("   ✅ Logout Successful!")
        print(f"   Response: {json.dumps(response, indent=2)}")
    else:
        print(f"   ❌ Logout Failed! Status: {status}")
        print(f"   Response: {json.dumps(response, indent=2)}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✨ Test Completed Successfully")
    print("=" * 60)

if __name__ == "__main__":
    main()
