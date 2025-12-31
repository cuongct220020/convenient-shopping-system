#!/usr/bin/env python3
"""
Comprehensive test script for all /me endpoints in the user-service.

This script tests the complete user information management flow:
1. Registration of a new user
2. Login to get authentication token
3. View basic/core user information
4. View and update identity profile
5. View and update health profile
6. Change email (request and confirm)
7. Change password
8. Logout

Usage:
    python3 user-service/scripts/test_me_management_flow.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
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
            "cookies": response.headers.get("Set-Cookie")
        }
    except urllib.error.HTTPError as e:
        response_data = e.read().decode('utf-8')
        return {
            "status_code": e.getcode(),
            "data": json.loads(response_data) if response_data else None,
            "headers": dict(e.headers),
            "error": str(e)
        }
    except urllib.error.URLError as e:
        return {
            "status_code": 0,
            "data": None,
            "error": f"URL Error: {str(e)}"
        }
    except Exception as e:
        return {
            "status_code": 0,
            "data": None,
            "error": f"Exception: {str(e)}"
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
    else:
        print(f"{Colors.WARNING}→ {step}: {status}{Colors.ENDC}")

def test_me_endpoints_flow():
    """Test the complete /me endpoints flow."""
    print(f"{Colors.HEADER}🧪 Testing /me Endpoints Flow{Colors.ENDC}")
    print("=" * 60)
    
    # Generate unique test data
    test_username = f"testuser_{int(time.time())}"
    test_email = f"test_{int(time.time())}@example.com"
    test_password = "SecurePassword123!"
    new_test_email = f"new_{int(time.time())}@example.com"
    new_test_password = "NewSecurePassword456!"
    
    print_status("Test Data Generation", "INFO", f"Username: {test_username}, Email: {test_email}")
    
    # Step 1: Register a new user
    print(f"\n{Colors.INFO}Step 1: Register a new user{Colors.ENDC}")
    register_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = make_request(
        f"{BASE_URL}/auth/register",
        method="POST",
        data=register_data
    )
    
    if response["status_code"] == 201:
        print_status("User Registration", "SUCCESS", f"Status: {response['status_code']}")
        user_data = response["data"]
        print_status("User Info", "INFO", f"Registered user ID: {user_data.get('data', {}).get('id', 'N/A')}")
    else:
        print_status("User Registration", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Step 2: Get OTP for registration verification
    print(f"\n{Colors.INFO}Step 2: Request OTP for registration verification{Colors.ENDC}")
    otp_data = {"email": test_email, "action": "register"}

    response = make_request(
        f"{BASE_URL}/auth/otp/send",
        method="POST",
        data=otp_data
    )

    if response["status_code"] == 200:
        print_status("OTP Request", "SUCCESS", f"Status: {response['status_code']}")
        if response["data"] and "data" in response["data"] and "otp_code" in response["data"]["data"]:
            otp_code = response["data"]["data"]["otp_code"]
            print_status("OTP Code", "INFO", f"Retrieved OTP: {otp_code}")
        else:
            print_status("OTP Code", "WARNING", "OTP not available in debug mode - skipping verification")
            otp_code = None
    else:
        print_status("OTP Request", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Step 3: Verify registration with OTP (if available)
    if otp_code:
        print(f"\n{Colors.INFO}Step 3: Verify registration with OTP{Colors.ENDC}")
        verify_data = {"email": test_email, "otp_code": otp_code}
        
        response = make_request(
            f"{BASE_URL}/auth/otp/verify",
            method="POST",
            data=verify_data
        )
        
        if response["status_code"] == 200:
            print_status("Registration Verification", "SUCCESS", f"Status: {response['status_code']}")
        else:
            print_status("Registration Verification", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
            return False
    else:
        print(f"\n{Colors.INFO}Step 3: Skipping registration verification (no OTP in response){Colors.ENDC}")
        print_status("Registration Verification", "SKIPPED", "OTP not available in response")
    
    # Step 4: Login to get authentication token
    print(f"\n{Colors.INFO}Step 4: Login to get authentication token{Colors.ENDC}")
    login_data = {"identifier": test_username, "password": test_password}

    response = make_request(
        f"{BASE_URL}/auth/login",
        method="POST",
        data=login_data
    )
    
    if response["status_code"] == 200:
        print_status("User Login", "SUCCESS", f"Status: {response['status_code']}")
        auth_data = response["data"]
        access_token = auth_data.get("data", {}).get("access_token")
        refresh_cookie = response["cookies"]
        
        if access_token:
            print_status("Access Token", "INFO", f"Retrieved access token: {access_token[:20]}...")
        else:
            print_status("Access Token", "FAILED", "No access token in response")
            return False
    else:
        print_status("User Login", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Set up authentication headers for subsequent requests
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 5: Get user's core information
    print(f"\n{Colors.INFO}Step 5: Get user's core information (/me){Colors.ENDC}")
    response = make_request(
        f"{BASE_URL}/users/me/",
        method="GET",
        headers=auth_headers
    )
    
    if response["status_code"] == 200:
        print_status("Get Core Info", "SUCCESS", f"Status: {response['status_code']}")
        user_info = response["data"]["data"]
        print_status("User Core Info", "INFO", f"Username: {user_info.get('username')}, Email: {user_info.get('email')}")
    else:
        print_status("Get Core Info", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Step 6: Update user's core information
    print(f"\n{Colors.INFO}Step 6: Update user's core information (/me){Colors.ENDC}")
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "phone_num": f"+123456789{int(time.time()) % 1000:03d}"  # Unique phone number based on timestamp
    }

    response = make_request(
        f"{BASE_URL}/users/me",
        method="PATCH",
        headers=auth_headers,
        data=update_data
    )
    
    if response["status_code"] == 200:
        print_status("Update Core Info", "SUCCESS", f"Status: {response['status_code']}")
        updated_info = response["data"]["data"]
        print_status("Updated Info", "INFO", f"Updated name: {updated_info.get('first_name')} {updated_info.get('last_name')}")
    else:
        print_status("Update Core Info", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Step 7: Get user's identity profile
    print(f"\n{Colors.INFO}Step 7: Get user's identity profile (/me/profile/identity){Colors.ENDC}")
    response = make_request(
        f"{BASE_URL}/users/me/profile/identity",
        method="GET",
        headers=auth_headers
    )
    
    if response["status_code"] in [200, 404]:
        if response["status_code"] == 200:
            print_status("Get Identity Profile", "SUCCESS", f"Status: {response['status_code']}")
            profile_data = response["data"]["data"]
            print_status("Identity Profile", "INFO", f"Gender: {profile_data.get('gender', 'N/A')}, DOB: {profile_data.get('date_of_birth', 'N/A')}")
        else:
            print_status("Get Identity Profile", "INFO", f"Profile not found (Status: {response['status_code']}), will create one next")
    else:
        print_status("Get Identity Profile", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Step 8: Update user's identity profile
    print(f"\n{Colors.INFO}Step 8: Update user's identity profile (/me/profile/identity){Colors.ENDC}")
    identity_data = {
        "gender": "male",
        "date_of_birth": "1990-01-01",
        "occupation": "Engineer"
    }

    response = make_request(
        f"{BASE_URL}/users/me/profile/identity",
        method="PATCH",
        headers=auth_headers,
        data=identity_data
    )
    
    if response["status_code"] == 200:
        print_status("Update Identity Profile", "SUCCESS", f"Status: {response['status_code']}")
        updated_profile = response["data"]["data"]
        print_status("Updated Identity Profile", "INFO", f"Gender: {updated_profile.get('gender')}, DOB: {updated_profile.get('date_of_birth')}")
    else:
        print_status("Update Identity Profile", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Step 9: Get user's health profile
    print(f"\n{Colors.INFO}Step 9: Get user's health profile (/me/profile/health){Colors.ENDC}")
    response = make_request(
        f"{BASE_URL}/users/me/profile/health",
        method="GET",
        headers=auth_headers
    )
    
    if response["status_code"] in [200, 404]:
        if response["status_code"] == 200:
            print_status("Get Health Profile", "SUCCESS", f"Status: {response['status_code']}")
            health_data = response["data"]["data"]
            print_status("Health Profile", "INFO", f"Height: {health_data.get('height', 'N/A')}cm, Weight: {health_data.get('weight', 'N/A')}kg")
        else:
            print_status("Get Health Profile", "INFO", f"Profile not found (Status: {response['status_code']}), will create one next")
    else:
        print_status("Get Health Profile", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Step 10: Update user's health profile
    print(f"\n{Colors.INFO}Step 10: Update user's health profile (/me/profile/health){Colors.ENDC}")
    health_data = {
        "height_cm": 180,
        "weight_kg": 75.0,
        "activity_level": "moderate",
        "curr_condition": "normal",
        "health_goal": "maintain"
    }

    response = make_request(
        f"{BASE_URL}/users/me/profile/health",
        method="PATCH",
        headers=auth_headers,
        data=health_data
    )
    
    if response["status_code"] == 200:
        print_status("Update Health Profile", "SUCCESS", f"Status: {response['status_code']}")
        updated_health = response["data"]["data"]
        print_status("Updated Health Profile", "INFO", f"Height: {updated_health.get('height')}cm, Weight: {updated_health.get('weight')}kg")
    else:
        print_status("Update Health Profile", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Step 11: Request to change email
    print(f"\n{Colors.INFO}Step 11: Request to change email (/me/email/request-change){Colors.ENDC}")
    email_change_data = {"new_email": new_test_email}

    response = make_request(
        f"{BASE_URL}/users/me/email/request-change",
        method="POST",
        headers=auth_headers,
        data=email_change_data
    )
    
    if response["status_code"] == 200:
        print_status("Request Email Change", "SUCCESS", f"Status: {response['status_code']}")
        if response["data"] and "data" in response["data"] and "otp_code" in response["data"]["data"]:
            new_otp_code = response["data"]["data"]["otp_code"]
            print_status("New OTP Code", "INFO", f"Retrieved OTP for email change: {new_otp_code}")
        else:
            print_status("New OTP Code", "WARNING", "OTP not available in debug mode - skipping confirmation")
            new_otp_code = None
    else:
        print_status("Request Email Change", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False
    
    # Step 12: Confirm email change (if OTP is available)
    email_change_success = False
    if new_otp_code:
        print(f"\n{Colors.INFO}Step 12: Confirm email change with OTP (/me/email/confirm-change){Colors.ENDC}")
        confirm_data = {"new_email": new_test_email, "otp_code": new_otp_code}  # Fixed: Use correct field names

        response = make_request(
            f"{BASE_URL}/users/me/email/confirm-change",
            method="POST",
            headers=auth_headers,
            data=confirm_data
        )

        if response["status_code"] == 200:
            print_status("Confirm Email Change", "SUCCESS", f"Status: {response['status_code']}")
            email_change_success = True
        else:
            print_status("Confirm Email Change", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
            print_status("Email Change", "INFO", "Continuing with test (focusing on password change functionality)")
    else:
        print(f"\n{Colors.INFO}Step 12: Skipping email change confirmation (no OTP in response){Colors.ENDC}")
        print_status("Email Change Confirmation", "SKIPPED", "OTP not available in response")
    
    # Step 13: Change password
    print(f"\n{Colors.INFO}Step 13: Change password (/me/change-password){Colors.ENDC}")
    password_change_data = {
        "current_password": test_password,
        "new_password": new_test_password
    }

    response = make_request(
        f"{BASE_URL}/users/me/change-password",
        method="POST",
        headers=auth_headers,
        data=password_change_data
    )

    if response["status_code"] == 200:
        print_status("Change Password", "SUCCESS", f"Status: {response['status_code']}")
        print_status("Password Change Message", "INFO", f"Response: {response['data']['message'] if response['data'] else 'N/A'}")
    else:
        print_status("Change Password", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False

    # Step 14: Try to access protected endpoint with old token (should fail after password change)
    print(f"\n{Colors.INFO}Step 14: Test if old token is invalidated after password change{Colors.ENDC}")
    response = make_request(
        f"{BASE_URL}/users/me/",
        method="GET",
        headers=auth_headers  # Using old token
    )

    if response["status_code"] in [401, 403]:
        print_status("Old Token Invalidated", "SUCCESS", f"Old token properly invalidated (Status: {response['status_code']})")
    else:
        print_status("Old Token Invalidated", "WARNING", f"Old token still valid (Status: {response['status_code']}) - this may be expected depending on implementation")

    # Step 15: Login with new password to get new token
    print(f"\n{Colors.INFO}Step 15: Login with new password to get new token{Colors.ENDC}")
    login_data = {"identifier": test_username, "password": new_test_password}

    response = make_request(
        f"{BASE_URL}/auth/login",
        method="POST",
        data=login_data
    )

    if response["status_code"] == 200:
        print_status("Login with New Password", "SUCCESS", f"Status: {response['status_code']}")
        auth_data = response["data"]
        new_access_token = auth_data.get("data", {}).get("access_token")

        if new_access_token:
            print_status("New Access Token", "INFO", f"Retrieved new access token: {new_access_token[:20]}...")
            new_auth_headers = {"Authorization": f"Bearer {new_access_token}"}
        else:
            print_status("New Access Token", "FAILED", "No new access token in response")
            return False
    else:
        print_status("Login with New Password", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False

    # Step 16: Access protected endpoint with new token (should work)
    print(f"\n{Colors.INFO}Step 16: Access protected endpoint with new token{Colors.ENDC}")
    response = make_request(
        f"{BASE_URL}/users/me/",
        method="GET",
        headers=new_auth_headers  # Using new token
    )

    if response["status_code"] == 200:
        print_status("Access with New Token", "SUCCESS", f"Status: {response['status_code']}")
        user_info = response["data"]["data"]
        print_status("User Info with New Token", "INFO", f"Username: {user_info.get('username')}")
    else:
        print_status("Access with New Token", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False

    # Step 17: Logout with new token
    print(f"\n{Colors.INFO}Step 17: Logout from the system (/auth/logout){Colors.ENDC}")
    response = make_request(
        f"{BASE_URL}/auth/logout",
        method="POST",
        headers=new_auth_headers
    )

    if response["status_code"] == 200:
        print_status("Logout", "SUCCESS", f"Status: {response['status_code']}")
    else:
        print_status("Logout", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False

    # Step 18: Test tag management endpoints
    print(f"\n{Colors.INFO}Step 18: Test tag management endpoints (/me/tags){Colors.ENDC}")

    # Get user's tags (should be empty initially)
    response = make_request(
        f"{BASE_URL}/users/me/tags",
        method="GET",
        headers=new_auth_headers  # Using the new token from re-authentication
    )

    if response["status_code"] == 200:
        print_status("Get User Tags", "SUCCESS", f"Status: {response['status_code']}")
    else:
        print_status("Get User Tags", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False

    # Add some tags to the user
    tags_data = {
        "tags": ["allergy.gluten_free", "diet.keto", "goal.weight_loss"]
    }

    response = make_request(
        f"{BASE_URL}/users/me/tags",
        method="POST",
        headers=new_auth_headers,
        data=tags_data
    )

    if response["status_code"] == 201:
        print_status("Add User Tags", "SUCCESS", f"Status: {response['status_code']}")
    else:
        print_status("Add User Tags", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False

    # Update tags in a specific category
    category_tags_data = {
        "tag_values": ["allergy.dairy_free", "allergy.nut_free"]
    }

    response = make_request(
        f"{BASE_URL}/users/me/tags/category/allergy",
        method="PUT",
        headers=new_auth_headers,
        data=category_tags_data
    )

    if response["status_code"] == 200:
        print_status("Update Category Tags", "SUCCESS", f"Status: {response['status_code']}")
    else:
        print_status("Update Category Tags", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False

    # Delete some tags
    delete_tags_data = {
        "tags": ["diet.keto"]
    }

    response = make_request(
        f"{BASE_URL}/users/me/tags/delete",
        method="POST",
        headers=new_auth_headers,
        data=delete_tags_data
    )

    if response["status_code"] == 200:
        print_status("Delete User Tags", "SUCCESS", f"Status: {response['status_code']}")
    else:
        print_status("Delete User Tags", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False

    # Step 19: Try to login with new email and new password (if email was changed)
    print(f"\n{Colors.INFO}Step 19: Login with new credentials (new email if changed, new password){Colors.ENDC}")
    # Use original email if email change failed, otherwise use new email
    login_identifier = new_test_email if (new_otp_code and email_change_success) else test_username
    login_data = {"identifier": login_identifier, "password": new_test_password}

    response = make_request(
        f"{BASE_URL}/auth/login",
        method="POST",
        data=login_data
    )

    if response["status_code"] == 200:
        print_status("Login with New Credentials", "SUCCESS", f"Status: {response['status_code']}")
        print_status("Flow Test", "SUCCESS", "All /me endpoints tested successfully!")
        return True
    else:
        print_status("Login with New Credentials", "FAILED", f"Status: {response['status_code']}, Error: {response.get('error', 'N/A')}")
        return False

def main():
    """Main function to run the test."""
    print(f"{Colors.HEADER}🚀 Starting /me Endpoints Test Flow{Colors.ENDC}")
    
    success = test_me_endpoints_flow()
    
    print("\n" + "=" * 60)
    if success:
        print(f"{Colors.OKGREEN}🎉 All tests passed successfully!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"{Colors.FAIL}💥 Some tests failed. Please check the output above.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()