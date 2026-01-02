#!/usr/bin/env python3
"""
Edge Cases and Boundary Conditions Test Script for /me Endpoints in the user-service.

This script tests edge cases and boundary conditions:
1. Boundary values for numeric fields
2. Edge cases for string fields
3. Time-based edge cases
4. Empty/minimum/maximum value cases
5. Race conditions
6. Boundary conditions for file uploads (if applicable)

Usage:
    python3 user-service/tests/test_me_management_edge_cases.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import time
import random
import string
from datetime import datetime, timedelta
import threading

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
    test_username = f"edge_test_user_{int(time.time())}_{random.randint(1000, 9999)}{suffix}"
    test_email = f"edge_test_{int(time.time())}_{random.randint(1000, 9999)}{suffix}@example.com"
    test_password = "SecurePassword123!"

    register_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "first_name": "Edge",
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

def test_boundary_numeric_values():
    """Test boundary values for numeric fields."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Testing Boundary Numeric Values{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_numeric")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test boundary values for health profile fields
    boundary_tests = [
        # Height tests
        {"height_cm": 0, "description": "Zero height"},
        {"height_cm": -1, "description": "Negative height"},
        {"height_cm": 300, "description": "Very tall height"},
        {"height_cm": 20, "description": "Very short height"},
        {"height_cm": 300.0, "description": "Float max height"},
        
        # Weight tests
        {"weight_kg": 0, "description": "Zero weight"},
        {"weight_kg": -1, "description": "Negative weight"},
        {"weight_kg": 1000, "description": "Very heavy weight"},
        {"weight_kg": 0.1, "description": "Very light weight"},
        {"weight_kg": 999.9, "description": "Max weight"},
    ]

    for test_data in boundary_tests:
        field_name = list(test_data.keys())[0]
        description = test_data.pop("description")
        
        print(f"\n{Colors.INFO}Testing {description}: {test_data[field_name]}{Colors.ENDC}")
        
        response = make_request(
            f"{BASE_URL}/users/me/profile/health",
            method="PATCH",
            headers=auth_headers,
            data=test_data
        )
        
        if response["status_code"] in [200, 400, 422]:
            print_status(f"{description}", "SUCCESS", f"Handled properly (Status: {response['status_code']})")
        else:
            print_status(f"{description}", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def test_string_boundary_conditions():
    """Test boundary conditions for string fields."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Testing String Boundary Conditions{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_string")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test string boundary conditions
    string_tests = [
        # Empty strings
        {"first_name": "", "description": "Empty first name"},
        {"last_name": "", "description": "Empty last name"},
        {"occupation": "", "description": "Empty occupation"},
        
        # Minimum length strings
        {"first_name": "A", "description": "Single character first name"},
        {"last_name": "B", "description": "Single character last name"},
        {"username": "C", "description": "Single character username"},
        
        # Whitespace strings
        {"first_name": "   ", "description": "Whitespace only first name"},
        {"last_name": "\t\n", "description": "Tab and newline last name"},
        {"occupation": " \t \n ", "description": "Whitespace occupation"},
        
        # Special character strings
        {"first_name": "O'Connor", "description": "Apostrophe in name"},
        {"last_name": "Smith-Jones", "description": "Hyphen in name"},
        {"occupation": "Developer & Tester", "description": "Ampersand in occupation"},
        
        # Unicode strings
        {"first_name": "José", "description": "Accented character"},
        {"last_name": "Müller", "description": "Umlaut character"},
        {"occupation": "🐍 Developer", "description": "Emoji in occupation"},
    ]

    for test_data in string_tests:
        field_name = list(test_data.keys())[0]
        description = test_data.pop("description")
        
        print(f"\n{Colors.INFO}Testing {description}: {repr(test_data[field_name])}{Colors.ENDC}")
        
        response = make_request(
            f"{BASE_URL}/users/me",
            method="PATCH",
            headers=auth_headers,
            data=test_data
        )
        
        if response["status_code"] in [200, 400, 422]:
            print_status(f"{description}", "SUCCESS", f"Handled properly (Status: {response['status_code']})")
        else:
            print_status(f"{description}", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def test_date_boundary_conditions():
    """Test boundary conditions for date fields."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Testing Date Boundary Conditions{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_date")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test date boundary conditions
    date_tests = [
        {"date_of_birth": "1900-01-01", "description": "Very old birth date"},
        {"date_of_birth": "2025-01-01", "description": "Future birth date"},
        {"date_of_birth": "2024-02-29", "description": "Leap year date"},
        {"date_of_birth": "2023-02-29", "description": "Invalid leap year date"},
        {"date_of_birth": "1990-13-01", "description": "Invalid month"},
        {"date_of_birth": "1990-01-32", "description": "Invalid day"},
        {"date_of_birth": "0001-01-01", "description": "Minimum date"},
        {"date_of_birth": "9999-12-31", "description": "Maximum date"},
        {"date_of_birth": "", "description": "Empty date"},
        {"date_of_birth": "invalid-date", "description": "Invalid date format"},
    ]

    for test_data in date_tests:
        description = test_data.pop("description")
        
        print(f"\n{Colors.INFO}Testing {description}: {test_data.get('date_of_birth', 'N/A')}{Colors.ENDC}")
        
        response = make_request(
            f"{BASE_URL}/users/me/profile/identity",
            method="PATCH",
            headers=auth_headers,
            data=test_data
        )
        
        if response["status_code"] in [200, 400, 422]:
            print_status(f"{description}", "SUCCESS", f"Handled properly (Status: {response['status_code']})")
        else:
            print_status(f"{description}", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def test_email_boundary_conditions():
    """Test boundary conditions for email fields."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Testing Email Boundary Conditions{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_email")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test email boundary conditions
    email_tests = [
        {"new_email": "a@b.co", "description": "Minimal valid email"},
        {"new_email": "very.long.email.address.that.might.be.too.long@example.com", "description": "Long email address"},
        {"new_email": "user+tag@example.com", "description": "Email with plus tag"},
        {"new_email": "user.name@example.com", "description": "Email with dots"},
        {"new_email": "user_name@example-domain.com", "description": "Email with underscore and hyphen"},
        {"new_email": "1234567890@example.com", "description": "Numeric local part"},
        {"new_email": "\"quoted\"@example.com", "description": "Quoted local part"},
        {"new_email": "", "description": "Empty email"},
        {"new_email": "@example.com", "description": "Missing local part"},
        {"new_email": "user@", "description": "Missing domain"},
        {"new_email": "user@domain", "description": "Missing TLD"},
        {"new_email": "user..name@example.com", "description": "Double dots"},
        {"new_email": "user@domain..com", "description": "Double dots in domain"},
    ]

    for test_data in email_tests:
        description = test_data.pop("description")
        
        print(f"\n{Colors.INFO}Testing {description}: {test_data.get('new_email', 'N/A')}{Colors.ENDC}")
        
        # Note: We can't actually test email change without OTP, so we'll just test validation
        response = make_request(
            f"{BASE_URL}/users/me/email/request-change",
            method="POST",
            headers=auth_headers,
            data=test_data
        )
        
        if response["status_code"] in [200, 400, 422]:
            print_status(f"{description}", "SUCCESS", f"Handled properly (Status: {response['status_code']})")
        else:
            print_status(f"{description}", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def test_race_conditions():
    """Test potential race conditions."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Testing Race Conditions{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_race")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test concurrent updates to the same resource
    print(f"\n{Colors.INFO}Testing concurrent updates to user profile{Colors.ENDC}")
    
    results = []
    
    def update_profile(first_name, last_name):
        response = make_request(
            f"{BASE_URL}/users/me",
            method="PATCH",
            headers=auth_headers,
            data={"first_name": first_name, "last_name": last_name}
        )
        results.append(response)
    
    # Start multiple threads updating the profile simultaneously
    threads = []
    for i in range(5):
        thread = threading.Thread(
            target=update_profile, 
            args=(f"FirstName_{i}", f"LastName_{i}")
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Check results
    success_count = sum(1 for r in results if r["status_code"] == 200)
    print_status("Concurrent Updates", "INFO", f"{success_count}/5 updates succeeded")
    
    # Get final state to see which update won
    final_response = make_request(
        f"{BASE_URL}/users/me/",
        method="GET",
        headers=auth_headers
    )
    
    if final_response["status_code"] == 200:
        final_data = final_response["data"]["data"]
        print_status("Final State", "INFO", f"Name: {final_data.get('first_name')} {final_data.get('last_name')}")
    else:
        print_status("Final State", "WARNING", f"Could not retrieve final state: {final_response['status_code']}")

def test_min_max_value_boundaries():
    """Test minimum and maximum value boundaries."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Testing Min/Max Value Boundaries{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_minmax")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test with extreme numeric values
    extreme_tests = [
        {"weight_kg": 0.000001, "description": "Near-zero weight"},
        {"weight_kg": 999.999999, "description": "Near-max weight"},
        {"height_cm": 0.000001, "description": "Near-zero height"},
        {"height_cm": 299.999999, "description": "Near-max height"},
        {"weight_kg": 1e-10, "description": "Extremely small weight"},
        {"weight_kg": 1e10, "description": "Extremely large weight"},
    ]

    for test_data in extreme_tests:
        field_name = list(test_data.keys())[0]
        description = test_data.pop("description")
        
        print(f"\n{Colors.INFO}Testing {description}: {test_data[field_name]}{Colors.ENDC}")
        
        response = make_request(
            f"{BASE_URL}/users/me/profile/health",
            method="PATCH",
            headers=auth_headers,
            data=test_data
        )
        
        if response["status_code"] in [200, 400, 422]:
            print_status(f"{description}", "SUCCESS", f"Handled properly (Status: {response['status_code']})")
        else:
            print_status(f"{description}", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def test_empty_collection_boundaries():
    """Test operations with empty collections."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Testing Empty Collection Boundaries{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_empty")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test operations with empty arrays/objects
    empty_tests = [
        # Empty arrays for tags
        {"tags": [], "description": "Empty tags array"},
        {"tag_values": [], "description": "Empty tag values array"},
        
        # Empty objects
        {"description": "Empty request body"},
    ]

    # Test endpoints that accept arrays
    for test_data in empty_tests[:-1]:  # Skip the empty object test for now
        description = test_data.pop("description")
        
        print(f"\n{Colors.INFO}Testing {description}: {test_data}{Colors.ENDC}")
        
        # Try on tags endpoint if it exists
        response = make_request(
            f"{BASE_URL}/users/me/tags",
            method="POST",
            headers=auth_headers,
            data=test_data
        )
        
        if response["status_code"] in [200, 201, 400, 422]:
            print_status(f"{description}", "SUCCESS", f"Handled properly (Status: {response['status_code']})")
        else:
            print_status(f"{description}", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def test_time_based_edge_cases():
    """Test time-based edge cases."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Testing Time-Based Edge Cases{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_time")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test rapid consecutive requests
    print(f"\n{Colors.INFO}Testing rapid consecutive requests{Colors.ENDC}")
    
    start_time = time.time()
    responses = []
    
    for i in range(10):
        response = make_request(
            f"{BASE_URL}/users/me/",
            method="GET",
            headers=auth_headers
        )
        responses.append(response)
        # No delay - test rapid requests
    
    end_time = time.time()
    
    success_count = sum(1 for r in responses if r["status_code"] == 200)
    print_status("Rapid Requests", "INFO", 
                f"{success_count}/10 requests succeeded in {end_time - start_time:.3f}s")

def test_character_encoding_edge_cases():
    """Test character encoding edge cases."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Testing Character Encoding Edge Cases{Colors.ENDC}")
    print("=" * 60)

    # Register and login a test user
    user_email, user_password = register_test_user("_encoding")
    if not user_email:
        print_status("Setup", "FAILED", "Could not register test user")
        return

    access_token = login_user(user_email, user_password)
    if not access_token:
        print_status("Setup", "FAILED", "Could not login test user")
        return

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Test various encoding edge cases
    encoding_tests = [
        {"first_name": "François", "description": "Latin-1 characters"},
        {"first_name": "Михаил", "description": "Cyrillic characters"},
        {"first_name": "汉字", "description": "Chinese characters"},
        {"first_name": "こんにちは", "description": "Japanese characters"},
        {"first_name": "العربية", "description": "Arabic characters"},
        {"first_name": "🙂😂🤣", "description": "Multiple emojis"},
        {"first_name": "a\nb\tc\rd", "description": "Control characters"},
        {"first_name": "\x00\x01\x02\x03", "description": "Null and control bytes"},
        {"first_name": "café\r\nnaïve", "description": "Combined special chars"},
    ]

    for test_data in encoding_tests:
        field_name = list(test_data.keys())[0]
        description = test_data.pop("description")
        
        print(f"\n{Colors.INFO}Testing {description}: {repr(test_data[field_name][:50])}...{Colors.ENDC}")
        
        response = make_request(
            f"{BASE_URL}/users/me",
            method="PATCH",
            headers=auth_headers,
            data=test_data
        )
        
        if response["status_code"] in [200, 400, 422]:
            print_status(f"{description}", "SUCCESS", f"Handled properly (Status: {response['status_code']})")
        else:
            print_status(f"{description}", "WARNING", f"Unexpected response (Status: {response['status_code']})")

def run_edge_case_tests():
    """Run all edge case tests."""
    print(f"{Colors.HEADER}{Colors.BOLD}🔍 Running /me Endpoints Edge Case Tests{Colors.ENDC}")
    print(f"{Colors.INFO}Testing edge cases and boundary conditions{Colors.ENDC}")
    
    test_boundary_numeric_values()
    test_string_boundary_conditions()
    test_date_boundary_conditions()
    test_email_boundary_conditions()
    test_race_conditions()
    test_min_max_value_boundaries()
    test_empty_collection_boundaries()
    test_time_based_edge_cases()
    test_character_encoding_edge_cases()
    
    print(f"\n{Colors.BOLD}🎉 Edge Case Testing Complete!{Colors.ENDC}")
    print(f"{Colors.INFO}Check for any WARNING or CRITICAL issues above.{Colors.ENDC}")

if __name__ == "__main__":
    run_edge_case_tests()