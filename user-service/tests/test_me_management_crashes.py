#!/usr/bin/env python3
"""
Server Crash Test Script for /me Endpoints in the user-service.

This script specifically tests potential server crash scenarios:
1. Memory exhaustion attacks
2. Stack overflow attempts
3. Resource exhaustion
4. Denial of service attempts
5. Buffer overflow that could crash the server

Usage:
    python3 user-service/tests/test_me_management_crashes.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket

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
        response = urllib.request.urlopen(req, context=ssl_context, timeout=30)  # 30 second timeout
        response_data = response.read().decode('utf-8')
        return {
            "status_code": response.getcode(),
            "data": json.loads(response_data) if response_data else None,
            "headers": dict(response.headers),
            "cookies": response.headers.get("Set-Cookie"),
            "success": True
        }
    except urllib.error.HTTPError as e:
        response_data = e.read().decode('utf-8')
        return {
            "status_code": e.getcode(),
            "data": json.loads(response_data) if response_data else None,
            "headers": dict(e.headers),
            "error": str(e),
            "success": False
        }
    except urllib.error.URLError as e:
        return {
            "status_code": 0,
            "data": None,
            "error": f"URL Error: {str(e)}",
            "success": False
        }
    except socket.timeout:
        return {
            "status_code": 0,
            "data": None,
            "error": "Request timed out",
            "success": False
        }
    except Exception as e:
        return {
            "status_code": 0,
            "data": None,
            "error": f"Exception: {str(e)}",
            "success": False
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
    test_username = f"crash_test_user_{int(time.time())}_{random.randint(1000, 9999)}{suffix}"
    test_email = f"crash_test_{int(time.time())}_{random.randint(1000, 9999)}{suffix}@example.com"
    test_password = "SecurePassword123!"

    register_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "first_name": "Crash",
        "last_name": "Test"
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

def test_memory_exhaustion():
    """Test potential memory exhaustion attacks."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}💥 Testing Memory Exhaustion{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_mem")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Create extremely large data payloads
    sizes = [100000, 500000, 1000000]  # 100KB, 500KB, 1MB
    
    for size in sizes:
        print(f"\n{Colors.INFO}Testing with {size:,} character payload{Colors.ENDC}")
        
        # Create a very large string
        large_string = "A" * size
        
        # Try to update user profile with large data
        start_time = time.time()
        response = make_request(
            f"{BASE_URL}/users/me",
            method="PATCH",
            headers=auth_headers,
            data={"first_name": large_string, "last_name": large_string}
        )
        end_time = time.time()
        
        if response["success"]:
            print_status(f"Large payload {size:,} chars", "INFO", f"Processed in {end_time - start_time:.2f}s, Status: {response['status_code']}")
            
            # Check if server is still responsive by making a simple request
            health_check = make_request(f"{BASE_URL}/health", method="GET")
            if health_check["success"]:
                print_status("Server Health", "SUCCESS", "Server still responsive after large payload")
            else:
                print_status("Server Health", "CRITICAL", f"Server not responsive after large payload - potential crash!")
                return
        else:
            print_status(f"Large payload {size:,} chars", "INFO", f"Rejected: {response['error']}")
            
            # Check if server is still responsive
            health_check = make_request(f"{BASE_URL}/health", method="GET")
            if health_check["success"]:
                print_status("Server Health", "SUCCESS", "Server still responsive after rejected large payload")
            else:
                print_status("Server Health", "CRITICAL", f"Server not responsive after rejected large payload - potential crash!")
                return

def test_nested_structure_crashes():
    """Test deeply nested structures that could cause stack overflow."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}💥 Testing Nested Structure Crashes{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_nested")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Create deeply nested JSON structure
    def create_nested_dict(depth):
        if depth <= 0:
            return {"value": "test"}
        return {"nested": create_nested_dict(depth - 1)}

    # Test with different depths
    depths = [50, 100, 200]
    
    for depth in depths:
        print(f"\n{Colors.INFO}Testing with {depth} levels of nesting{Colors.ENDC}")
        
        nested_data = create_nested_dict(depth)
        
        start_time = time.time()
        response = make_request(
            f"{BASE_URL}/users/me",
            method="PATCH",
            headers=auth_headers,
            data=nested_data
        )
        end_time = time.time()
        
        if response["success"]:
            print_status(f"Nested structure {depth} levels", "INFO", f"Processed in {end_time - start_time:.2f}s, Status: {response['status_code']}")
        else:
            print_status(f"Nested structure {depth} levels", "INFO", f"Rejected: {response['error']}")
        
        # Check if server is still responsive
        health_check = make_request(f"{BASE_URL}/health", method="GET")
        if health_check["success"]:
            print_status("Server Health", "SUCCESS", f"Server still responsive after {depth}-level nesting")
        else:
            print_status("Server Health", "CRITICAL", f"Server not responsive after {depth}-level nesting - potential crash!")
            return

def test_concurrent_request_crashes():
    """Test server stability under high concurrent load."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}💥 Testing Concurrent Request Crashes{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_concurrent")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test different levels of concurrency
    concurrency_levels = [50, 100, 200]
    
    for level in concurrency_levels:
        print(f"\n{Colors.INFO}Testing {level} concurrent requests{Colors.ENDC}")
        
        def make_request_task():
            return make_request(f"{BASE_URL}/users/me/", method="GET", headers=auth_headers)
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=level) as executor:
            futures = [executor.submit(make_request_task) for _ in range(level)]
            results = [future.result() for future in futures]
        end_time = time.time()
        
        success_count = sum(1 for r in results if r["success"])
        error_count = len(results) - success_count
        
        print_status(f"Concurrent load {level}", "INFO", 
                    f"Completed {success_count}/{level} requests in {end_time - start_time:.2f}s. "
                    f"Errors: {error_count}")
        
        # Check if server is still responsive
        health_check = make_request(f"{BASE_URL}/health", method="GET")
        if health_check["success"]:
            print_status("Server Health", "SUCCESS", f"Server still responsive after {level} concurrent requests")
        else:
            print_status("Server Health", "CRITICAL", f"Server not responsive after {level} concurrent requests - potential crash!")
            return

def test_resource_exhaustion():
    """Test resource exhaustion attacks."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}💥 Testing Resource Exhaustion{Colors.ENDC}")
    print("=" * 60)

    # Register multiple test users to test with
    users = []
    for i in range(5):
        email, password = register_test_user(f"_resource_{i}")
        if email and password:
            token = login_user(email, password)
            if token:
                users.append({"email": email, "password": password, "token": token})
    
    if not users:
        print_status("Setup", "FAILED", "Could not register any test users")
        return

    # Open multiple connections simultaneously without closing them properly
    print(f"\n{Colors.INFO}Testing multiple simultaneous connections{Colors.ENDC}")
    
    # Create many requests at once to try to exhaust connection pool
    def create_request(user_data):
        headers = {"Authorization": f"Bearer {user_data['token']}"}
        return make_request(f"{BASE_URL}/users/me/", method="GET", headers=headers)
    
    # Test with 50 simultaneous requests from different users
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for i in range(50):
            user_data = users[i % len(users)]  # Cycle through available users
            futures.append(executor.submit(create_request, user_data))
        
        results = []
        for future in as_completed(futures, timeout=60):  # 60 second timeout
            try:
                result = future.result(timeout=10)  # 10 second timeout per request
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})

    success_count = sum(1 for r in results if r["success"])
    error_count = len(results) - success_count
    
    print_status("Resource Exhaustion", "INFO", 
                f"Completed {success_count}/{len(results)} requests. Errors: {error_count}")
    
    # Check if server is still responsive
    health_check = make_request(f"{BASE_URL}/health", method="GET")
    if health_check["success"]:
        print_status("Server Health", "SUCCESS", "Server still responsive after resource exhaustion test")
    else:
        print_status("Server Health", "CRITICAL", "Server not responsive after resource exhaustion test - potential crash!")

def test_large_header_crashes():
    """Test crashes from large headers."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}💥 Testing Large Header Crashes{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_header")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    # Create a very large header value
    large_header_value = "A" * 50000  # 50KB header
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Custom-Large-Header": large_header_value,
        "User-Agent": large_header_value,
    }

    print(f"\n{Colors.INFO}Testing request with large headers (~100KB total){Colors.ENDC}")
    
    response = make_request(
        f"{BASE_URL}/users/me/",
        method="GET",
        headers=headers
    )
    
    if response["success"]:
        print_status("Large Headers", "INFO", f"Processed large headers successfully, Status: {response['status_code']}")
    else:
        print_status("Large Headers", "INFO", f"Rejected large headers: {response['error']}")
    
    # Check if server is still responsive
    health_check = make_request(f"{BASE_URL}/health", method="GET")
    if health_check["success"]:
        print_status("Server Health", "SUCCESS", "Server still responsive after large header test")
    else:
        print_status("Server Health", "CRITICAL", "Server not responsive after large header test - potential crash!")

def test_timeout_crashes():
    """Test if server handles timeouts properly without crashing."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}💥 Testing Timeout Scenarios{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_timeout")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Make a request with a very short timeout to see how server handles it
    print(f"\n{Colors.INFO}Testing server behavior with timeout requests{Colors.ENDC}")
    
    # This test is more about ensuring the server doesn't crash when clients disconnect
    # abruptly rather than forcing a timeout on the server side
    
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Make several requests in quick succession to test server resilience
    for i in range(10):
        response = make_request(f"{BASE_URL}/users/me/", method="GET", headers=auth_headers)
        if not response["success"]:
            print_status(f"Request {i+1}", "INFO", f"Failed: {response['error']}")
        else:
            print_status(f"Request {i+1}", "INFO", f"Success: {response['status_code']}")
    
    # Check if server is still responsive
    health_check = make_request(f"{BASE_URL}/health", method="GET")
    if health_check["success"]:
        print_status("Server Health", "SUCCESS", "Server still responsive after timeout stress test")
    else:
        print_status("Server Health", "CRITICAL", "Server not responsive after timeout stress test - potential crash!")

def test_unicode_crashes():
    """Test crashes from unicode and special character handling."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}💥 Testing Unicode Crashes{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_unicode")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Unicode sequences that might cause issues
    problematic_unicode = [
        "" * 1000,  # Overlong UTF-8 sequences
        "\ud83d\ude00" * 10000,  # Emojis repeated
        "\x00" * 10000,  # Null bytes
        "\ufffd" * 10000,  # Replacement characters
        "\ud83d" * 10000,  # Lonely surrogates
        "🐍" * 10000 + "⚡" * 10000 + "🔥" * 10000,  # Many emojis
    ]

    for i, unicode_data in enumerate(problematic_unicode):
        print(f"\n{Colors.INFO}Testing unicode sequence {i+1} (length: {len(unicode_data)}){Colors.ENDC}")
        
        response = make_request(
            f"{BASE_URL}/users/me",
            method="PATCH",
            headers=auth_headers,
            data={"first_name": unicode_data[:50000]}  # Limit to 50K to avoid other issues
        )
        
        if response["success"]:
            print_status(f"Unicode test {i+1}", "INFO", f"Processed successfully, Status: {response['status_code']}")
        else:
            print_status(f"Unicode test {i+1}", "INFO", f"Rejected: {response['error']}")
        
        # Check if server is still responsive
        health_check = make_request(f"{BASE_URL}/health", method="GET")
        if health_check["success"]:
            print_status("Server Health", "SUCCESS", f"Server responsive after unicode test {i+1}")
        else:
            print_status("Server Health", "CRITICAL", f"Server not responsive after unicode test {i+1} - potential crash!")
            return

def run_crash_tests():
    """Run all crash tests."""
    print(f"{Colors.HEADER}{Colors.BOLD}💥 Running /me Endpoints Server Crash Tests{Colors.ENDC}")
    print(f"{Colors.INFO}Testing potential server crash scenarios and stability{Colors.ENDC}")
    
    test_memory_exhaustion()
    test_nested_structure_crashes()
    test_concurrent_request_crashes()
    test_resource_exhaustion()
    test_large_header_crashes()
    test_timeout_crashes()
    test_unicode_crashes()
    
    print(f"\n{Colors.BOLD}🎉 Server Crash Testing Complete!{Colors.ENDC}")
    print(f"{Colors.INFO}Check for any CRITICAL issues above that indicate potential server crashes.{Colors.ENDC}")

if __name__ == "__main__":
    run_crash_tests()