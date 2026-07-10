#!/usr/bin/env python3
"""
Idempotency Verification Test Script

This script verifies that the idempotency mechanism works correctly for the registration endpoint.
It simulates a client sending duplicate requests with the same Idempotency-Key.

Scenario:
1. Generate a random user and a unique Idempotency-Key.
2. Send Request A (Register) -> Expect 201 Created.
3. Send Request A again (duplicate) with SAME Key -> Expect 201 Created (Cached).
4. Verify response bodies are identical.
5. Verify that a second registration *without* the key (or with a new key) would typically fail 
   (due to duplicate email) or succeed (if different user).

Usage:
    python3 user-service/tests/test_idempotency_flow.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import random
import uuid
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

def run_idempotency_test():
    """Run the idempotency verification test."""
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 Idempotency Verification Test{Colors.ENDC}")
    print(f"{Colors.INFO}Target Endpoint: {BASE_URL}/auth/register{Colors.ENDC}")
    
    # Generate random values for this test run
    rnd = random.randint(10000, 99999)
    email = f"idem_test_{rnd}@example.com"
    username = f"idem_user_{rnd}"
    password = "SecurePassword123!"
    
    # Generate a unique Idempotency Key
    idempotency_key = str(uuid.uuid4())
    
    print(f"\n{Colors.INFO}Test Data:{Colors.ENDC}")
    print(f"  Email: {email}")
    print(f"  Key:   {idempotency_key}")
    
    payload = {
        "username": username, 
        "email": email, 
        "password": password,
        "first_name": "Idem", 
        "last_name": "Tester"
    }

    # ---------------------------------------------------------
    # Step 1: First Request
    # ---------------------------------------------------------
    print(f"\n{Colors.INFO}[1] 🚀 Sending First Request (Original)...{Colors.ENDC}")
    start_time = time.time()
    status1, _, response1 = make_request(
        f"{BASE_URL}/auth/register", 
        "POST", 
        payload, 
        headers={"Idempotency-Key": idempotency_key}
    )
    duration1 = time.time() - start_time

    if status1 == 201:
        user_id = response1.get('data', {}).get('id')
        print(f"{Colors.OKGREEN}✓ First Request Success (User ID: {user_id}){Colors.ENDC}")
        print(f"  Time taken: {duration1:.3f}s")
    else:
        print(f"{Colors.FAIL}❌ First Request Failed: {response1}{Colors.ENDC}")
        return False

    # ---------------------------------------------------------
    # Step 2: Second Request (Duplicate)
    # ---------------------------------------------------------
    print(f"\n{Colors.INFO}[2] 🔄 Sending Second Request (Duplicate with SAME Key)...{Colors.ENDC}")
    start_time = time.time()
    status2, _, response2 = make_request(
        f"{BASE_URL}/auth/register", 
        "POST", 
        payload, 
        headers={"Idempotency-Key": idempotency_key}
    )
    duration2 = time.time() - start_time

    # ---------------------------------------------------------
    # Step 3: Verification
    # ---------------------------------------------------------
    print(f"\n{Colors.INFO}[3] 🕵️  Verifying Results...{Colors.ENDC}")

    # Check Status Code
    if status2 == 201:
        print(f"{Colors.OKGREEN}✓ Second Request returned 201 Created (As expected for idempotent success){Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Second Request returned {status2} (Expected 201){Colors.ENDC}")
        print(f"  Response: {response2}")
        return False

    # Check Response Body Content
    # We compare the 'data' part mainly.
    data1 = response1.get('data', {})
    data2 = response2.get('data', {})

    if data1 == data2:
        print(f"{Colors.OKGREEN}✓ Response bodies are IDENTICAL{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Response bodies differ! Idempotency failed?{Colors.ENDC}")
        print(f"  Response 1: {data1}")
        print(f"  Response 2: {data2}")
        return False
        
    # Check Timing (Optional but interesting)
    # Cached response should typically be faster than creating a user (DB write + Email/OTP trigger)
    # But locally the diff might be negligible.
    print(f"  Time 1: {duration1:.3f}s | Time 2: {duration2:.3f}s")
    if duration2 < duration1:
        print(f"{Colors.OKGREEN}✓ Second request was faster (likely cached){Colors.ENDC}")

    # ---------------------------------------------------------
    # Step 4: Control Test (What happens without Idempotency?)
    # ---------------------------------------------------------
    print(f"\n{Colors.INFO}[4] 🧪 Control Test: Trying to register SAME email with NEW Key...{Colors.ENDC}")
    new_key = str(uuid.uuid4())
    status3, _, response3 = make_request(
        f"{BASE_URL}/auth/register", 
        "POST", 
        payload, 
        headers={"Idempotency-Key": new_key}
    )

    if status3 != 201:
        print(f"{Colors.OKGREEN}✓ Request failed as expected (Status: {status3}){Colors.ENDC}")
        print(f"  Reason: {response3.get('message') or response3}")
        print(f"{Colors.INFO}  (This confirms that the previous success was indeed due to Idempotency masking the duplicate error){Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠️  Unexpected Success: We created a duplicate user? Check DB constraints.{Colors.ENDC}")

    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 IDEMPOTENCY VERIFIED SUCCESSFULLY!{Colors.ENDC}")
    return True

if __name__ == "__main__":
    success = run_idempotency_test()
    if not success:
        sys.exit(1)
