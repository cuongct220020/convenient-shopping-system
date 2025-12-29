#!/usr/bin/env python3
"""
Script to test the refresh token flow, including token rotation and reuse prevention.

Usage:
    python3 user-service/scripts/test_refresh_token_flow.py

Requirements:
    - User Service and Kong Gateway must be running.
    - A user must exist (e.g., run create_admin_user.py).
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
from http.client import HTTPMessage
from typing import Tuple, Any, List, Optional, Dict


# --- Configuration ---
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
LOGIN_ENDPOINT = "/api/v1/user-service/auth/login"
REFRESH_ENDPOINT = "/api/v1/user-service/auth/refresh-token"
USERNAME = os.getenv("ADMIN_USERNAME", "admin")
PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")


def make_request(
    url: str,
    method: str = "POST",
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None
) -> Tuple[int, HTTPMessage, Any]:
    """Helper function to make HTTP requests, returning status, headers, and body."""
    if headers is None:
        headers = {}

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
            json_body = json.loads(response_body) if response_body else {}
            return response.status, response.headers, json_body
    except urllib.error.HTTPError as e:
        response_body = e.read().decode('utf-8')
        try:
            body_json = json.loads(response_body)
        except json.JSONDecodeError:
            body_json = {"raw_error": response_body}
        return e.code, e.headers, body_json
    except urllib.error.URLError as e:
        print(f"❌ Connection Error to {url}: {e.reason}")
        return 0, HTTPMessage(), None


def get_cookie_value(headers: HTTPMessage, cookie_name: str) -> Optional[str]:
    """Extracts a cookie value from the 'Set-Cookie' header."""
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


def main():
    """Main function to run the test scenario."""
    print("=" * 60)
    print(f"🧪 Testing Refresh Token Flow via Kong Gateway")
    print(f"   URL: {GATEWAY_URL}")
    print(f"   User: {USERNAME}")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Login to get the initial refresh token
    # ---------------------------------------------------------
    print("\n1️⃣  Step 1: Logging in to get initial tokens...")
    login_url = f"{GATEWAY_URL}{LOGIN_ENDPOINT}"
    login_payload = {"identifier": USERNAME, "password": PASSWORD}
    status, headers, response = make_request(login_url, "POST", login_payload)

    if status == 0:
        print("   -> Could not connect to Gateway. Is it running?")
        sys.exit(1)

    if status != 200:
        print(f"   ❌ Login Failed! Status: {status}")
        print(f"   Response: {json.dumps(response, indent=2)}")
        sys.exit(1)

    old_refresh_token = get_cookie_value(headers, "refresh_token")
    if not old_refresh_token:
        print("   ❌ Error: 'refresh_token' cookie not found in login response.")
        print(f"   Headers: {headers}")
        sys.exit(1)

    print("   ✅ Login Successful!")
    print(f"   🔑 Received initial Refresh Token (len={len(old_refresh_token)})")

    # ---------------------------------------------------------
    # 2. Use the refresh token to get a new access token
    # ---------------------------------------------------------
    print("\n2️⃣  Step 2: Using refresh token to get a new access token...")
    refresh_url = f"{GATEWAY_URL}{REFRESH_ENDPOINT}"
    refresh_headers = {"Cookie": f"refresh_token={old_refresh_token}"}
    status, headers, response = make_request(refresh_url, "POST", headers=refresh_headers)

    if status != 200:
        print(f"   ❌ Token Refresh Failed! Status: {status}")
        print(f"   Response: {json.dumps(response, indent=2)}")
        sys.exit(1)

    new_access_token = response.get('data', {}).get('access_token')
    new_refresh_token = get_cookie_value(headers, "refresh_token")

    if not new_access_token or not new_refresh_token:
        print("   ❌ Error: Did not receive new access and refresh tokens.")
        print(f"   Response: {json.dumps(response, indent=2)}")
        print(f"   Headers: {headers}")
        sys.exit(1)

    if new_refresh_token == old_refresh_token:
        print("   ❌ Error: Refresh token was not rotated! This is a security risk.")
        sys.exit(1)

    print("   ✅ Token Refresh Successful!")
    print(f"   🔑 Received new Access Token (len={len(new_access_token)})")
    print(f"   🔄 Received new, rotated Refresh Token (len={len(new_refresh_token)})")

    # ---------------------------------------------------------
    # 3. Attempt to reuse the old refresh token
    # ---------------------------------------------------------
    print("\n3️⃣  Step 3: Attempting to reuse the original (revoked) refresh token...")
    # We use the same headers as before, containing the `old_refresh_token`
    status, headers, response = make_request(refresh_url, "POST", headers=refresh_headers)

    if status == 401:
        print("   ✅ Correctly received '401 Unauthorized' as expected.")
        clearing_cookie = get_cookie_value(headers, "refresh_token")
        if clearing_cookie == '""' or clearing_cookie is None:
            print("   🍪 Server correctly sent a header to clear the invalid cookie.")
        else:
            print(f"   ⚠️ Server did not properly clear the cookie. Value: {clearing_cookie}")

    else:
        print(f"   ❌ Incorrect Behavior: Expected 401, but got {status}.")
        print("      The service may not be revoking used refresh tokens correctly.")
        sys.exit(1)


    print("\n" + "=" * 60)
    print("✨ Refresh Token Flow Test Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
