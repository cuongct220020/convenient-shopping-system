#!/usr/bin/env python3
"""
Script to test the complete User Tags Management Flow via Kong Gateway.

This script tests the full user tags management flow:
1. Login to get authentication token
2. Get current user's tags
3. Add tags to user
4. Update tags in a specific category
5. Delete specific tags
6. Verify all operations worked correctly

Usage:
    python3 user-service/scripts/test_user_tags_flow.py
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import random
import time
import uuid
from typing import Dict, Any, Optional, Tuple

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
BASE_URL = f"{GATEWAY_URL}/api/v1/user-service"

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    INFO = '\033[94m'
    BOLD = '\033[1m'

def make_request(url: str, method: str = "GET", data: Optional[Dict] = None, headers: Optional[Dict] = None, auth_token: Optional[str] = None) -> Tuple[int, Any]:
    """
    Make an HTTP request with proper headers and error handling.
    
    Args:
        url: The URL to make the request to
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        data: JSON data to send in the request body
        headers: Additional headers to include
        auth_token: Bearer token for authentication
    
    Returns:
        Tuple of (status_code, response_data)
    """
    if headers is None:
        headers = {}

    # Add authentication header if token provided
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    # Prepare request data
    encoded_data = None
    if data and method in ["POST", "PUT", "PATCH"]:
        headers["Content-Type"] = "application/json"
        if isinstance(data, dict):
            encoded_data = json.dumps(data).encode('utf-8')
        else:
            encoded_data = json.dumps(data).encode('utf-8')

    # Create request object
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)

    # Create SSL context that doesn't verify certificates (for local development)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        response = urllib.request.urlopen(req, context=ssl_context)
        response_data = response.read().decode('utf-8')
        status_code = response.getcode()
        
        # Parse JSON response if possible
        try:
            json_data = json.loads(response_data) if response_data.strip() else {}
        except json.JSONDecodeError:
            json_data = {"raw_response": response_data}
        
        return status_code, json_data
    except urllib.error.HTTPError as e:
        response_body = e.read().decode('utf-8')
        try:
            body_json = json.loads(response_body) if response_body.strip() else {}
        except json.JSONDecodeError:
            body_json = {"raw_error": response_body}
        return e.code, body_json
    except urllib.error.URLError as e:
        print(f"{Colors.FAIL}❌ Connection Error to {url}: {e.reason}{Colors.ENDC}")
        return 0, {"error": f"Connection failed: {e.reason}"}
    except Exception as e:
        print(f"{Colors.FAIL}❌ Unexpected Error: {e}{Colors.ENDC}")
        return 0, {"error": f"Unexpected error: {str(e)}"}

def login_user(identifier: str, password: str) -> Optional[str]:
    """
    Login user and return authentication token.

    Args:
        identifier: User's username or email
        password: User's password

    Returns:
        Authentication token if successful, None otherwise
    """
    print(f"{Colors.INFO}🔐 Logging in user: {identifier}{Colors.ENDC}")

    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "identifier": identifier,
        "password": password
    }

    print(f"{Colors.INFO}📤 Sending login request to: {login_url}{Colors.ENDC}")
    print(f"{Colors.INFO}📤 Request data: {json.dumps(login_data, indent=2)}{Colors.ENDC}")

    status_code, response = make_request(login_url, "POST", login_data)

    print(f"{Colors.INFO}📥 Response status: {status_code}{Colors.ENDC}")
    print(f"{Colors.INFO}📥 Response data: {json.dumps(response, indent=2)}{Colors.ENDC}")

    if status_code == 200 and 'data' in response and 'access_token' in response['data']:
        print(f"{Colors.OKGREEN}✅ Login successful!{Colors.ENDC}")
        return response['data']['access_token']
    else:
        print(f"{Colors.FAIL}❌ Login failed with status {status_code}: {response}{Colors.ENDC}")
        return None

def get_user_tags(auth_token: str) -> Optional[Dict]:
    """
    Get current user's tags.
    
    Args:
        auth_token: Authentication token
    
    Returns:
        User tags data if successful, None otherwise
    """
    print(f"{Colors.INFO}📋 Getting user tags...{Colors.ENDC}")
    
    tags_url = f"{BASE_URL}/users/me/tags"
    
    print(f"{Colors.INFO}📤 Sending GET request to: {tags_url}{Colors.ENDC}")
    
    status_code, response = make_request(tags_url, "GET", headers={}, auth_token=auth_token)
    
    print(f"{Colors.INFO}📥 Response status: {status_code}{Colors.ENDC}")
    print(f"{Colors.INFO}📥 Response data: {json.dumps(response, indent=2)}{Colors.ENDC}")
    
    if status_code == 200:
        print(f"{Colors.OKGREEN}✅ Successfully retrieved user tags{Colors.ENDC}")
        return response
    else:
        print(f"{Colors.FAIL}❌ Failed to get user tags: {response}{Colors.ENDC}")
        return None

def add_user_tags(auth_token: str, tag_values: list) -> Optional[Dict]:
    """
    Add tags to user.
    
    Args:
        auth_token: Authentication token
        tag_values: List of tag values to add
    
    Returns:
        Response data if successful, None otherwise
    """
    print(f"{Colors.INFO}🏷️  Adding tags: {tag_values}{Colors.ENDC}")
    
    tags_url = f"{BASE_URL}/users/me/tags"
    request_data = {
        "tag_values": tag_values
    }
    
    print(f"{Colors.INFO}📤 Sending POST request to: {tags_url}{Colors.ENDC}")
    print(f"{Colors.INFO}📤 Request data: {json.dumps(request_data, indent=2)}{Colors.ENDC}")
    
    status_code, response = make_request(tags_url, "POST", request_data, auth_token=auth_token)
    
    print(f"{Colors.INFO}📥 Response status: {status_code}{Colors.ENDC}")
    print(f"{Colors.INFO}📥 Response data: {json.dumps(response, indent=2)}{Colors.ENDC}")
    
    if status_code in [200, 201]:
        print(f"{Colors.OKGREEN}✅ Successfully added tags{Colors.ENDC}")
        return response
    else:
        print(f"{Colors.FAIL}❌ Failed to add tags: {response}{Colors.ENDC}")
        return None

def update_category_tags(auth_token: str, category: str, tag_values: list) -> Optional[Dict]:
    """
    Update tags in a specific category.
    
    Args:
        auth_token: Authentication token
        category: Tag category to update
        tag_values: List of tag values to set for this category
    
    Returns:
        Response data if successful, None otherwise
    """
    print(f"{Colors.INFO}🔄 Updating category '{category}' tags: {tag_values}{Colors.ENDC}")
    
    tags_url = f"{BASE_URL}/users/me/tags/category/{category}"
    request_data = {
        "category": category,
        "tag_values": tag_values
    }
    
    print(f"{Colors.INFO}📤 Sending PUT request to: {tags_url}{Colors.ENDC}")
    print(f"{Colors.INFO}📤 Request data: {json.dumps(request_data, indent=2)}{Colors.ENDC}")
    
    status_code, response = make_request(tags_url, "PUT", request_data, auth_token=auth_token)
    
    print(f"{Colors.INFO}📥 Response status: {status_code}{Colors.ENDC}")
    print(f"{Colors.INFO}📥 Response data: {json.dumps(response, indent=2)}{Colors.ENDC}")
    
    if status_code == 200:
        print(f"{Colors.OKGREEN}✅ Successfully updated category '{category}' tags{Colors.ENDC}")
        return response
    else:
        print(f"{Colors.FAIL}❌ Failed to update category '{category}' tags: {response}{Colors.ENDC}")
        return None

def delete_user_tags(auth_token: str, tag_values: list) -> Optional[Dict]:
    """
    Delete specific tags from user.
    
    Args:
        auth_token: Authentication token
        tag_values: List of tag values to delete
    
    Returns:
        Response data if successful, None otherwise
    """
    print(f"{Colors.INFO}🗑️  Deleting tags: {tag_values}{Colors.ENDC}")
    
    tags_url = f"{BASE_URL}/users/me/tags/delete"
    request_data = {
        "tag_values": tag_values
    }
    
    print(f"{Colors.INFO}📤 Sending POST request to: {tags_url}{Colors.ENDC}")
    print(f"{Colors.INFO}📤 Request data: {json.dumps(request_data, indent=2)}{Colors.ENDC}")
    
    status_code, response = make_request(tags_url, "POST", request_data, auth_token=auth_token)
    
    print(f"{Colors.INFO}📥 Response status: {status_code}{Colors.ENDC}")
    print(f"{Colors.INFO}📥 Response data: {json.dumps(response, indent=2)}{Colors.ENDC}")
    
    if status_code == 200:
        print(f"{Colors.OKGREEN}✅ Successfully deleted tags{Colors.ENDC}")
        return response
    else:
        print(f"{Colors.FAIL}❌ Failed to delete tags: {response}{Colors.ENDC}")
        return None

def register_user(username: str, email: str, password: str, first_name: str = "Test", last_name: str = "User") -> tuple:
    """
    Register a new user for testing.

    Args:
        username: User's username
        email: User's email
        password: User's password
        first_name: User's first name
        last_name: User's last name

    Returns:
        Tuple of (success: bool, user_id: str or None)
    """
    print(f"{Colors.INFO}📝 Registering new user: {username}{Colors.ENDC}")

    register_url = f"{BASE_URL}/auth/register"
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name
    }

    print(f"{Colors.INFO}📤 Sending registration request to: {register_url}{Colors.ENDC}")
    print(f"{Colors.INFO}📤 Request data: {json.dumps(register_data, indent=2)}{Colors.ENDC}")

    status_code, response = make_request(register_url, "POST", register_data)

    print(f"{Colors.INFO}📥 Response status: {status_code}{Colors.ENDC}")
    print(f"{Colors.INFO}📥 Response data: {json.dumps(response, indent=2)}{Colors.ENDC}")

    if status_code in [200, 201] and 'data' in response and 'user_id' in response['data']:
        print(f"{Colors.OKGREEN}✅ Registration successful!{Colors.ENDC}")
        user_id = response['data']['user_id']
        return True, user_id
    else:
        print(f"{Colors.WARNING}⚠️  Registration status {status_code}: {response}{Colors.ENDC}")
        # If user already exists, that's OK for our test
        if "already exists" in str(response).lower() or status_code == 409:
            print(f"{Colors.INFO}ℹ️  User already exists, continuing with existing user{Colors.ENDC}")
            return True, None
        return False, None

def activate_user_with_admin(admin_token: str, user_id: str) -> bool:
    """
    Activate a user account using admin token.

    Args:
        admin_token: Admin authentication token
        user_id: ID of user to activate

    Returns:
        True if activation successful, False otherwise
    """
    print(f"{Colors.INFO}🔓 Activating user account: {user_id}{Colors.ENDC}")

    activate_url = f"{BASE_URL}/admin/users/{user_id}"
    activate_data = {
        "is_active": True
    }

    headers = {"Authorization": f"Bearer {admin_token}"}

    print(f"{Colors.INFO}📤 Sending activation request to: {activate_url}{Colors.ENDC}")
    print(f"{Colors.INFO}📤 Request data: {json.dumps(activate_data, indent=2)}{Colors.ENDC}")

    status_code, response = make_request(activate_url, "PUT", activate_data, headers=headers)

    print(f"{Colors.INFO}📥 Response status: {status_code}{Colors.ENDC}")
    print(f"{Colors.INFO}📥 Response data: {json.dumps(response, indent=2)}{Colors.ENDC}")

    if status_code == 200:
        print(f"{Colors.OKGREEN}✅ User activation successful!{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}❌ User activation failed: {response}{Colors.ENDC}")
        return False

def get_admin_token() -> Optional[str]:
    """
    Get admin token for administrative operations.

    Returns:
        Admin token if successful, None otherwise
    """
    print(f"{Colors.INFO}🔐 Getting admin token for user activation{Colors.ENDC}")

    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "identifier": "admin",
        "password": "admin"
    }

    print(f"{Colors.INFO}📤 Sending admin login request to: {login_url}{Colors.ENDC}")
    print(f"{Colors.INFO}📤 Request data: {json.dumps(login_data, indent=2)}{Colors.ENDC}")

    status_code, response = make_request(login_url, "POST", login_data)

    print(f"{Colors.INFO}📥 Response status: {status_code}{Colors.ENDC}")
    print(f"{Colors.INFO}📥 Response data: {json.dumps(response, indent=2)}{Colors.ENDC}")

    if status_code == 200 and 'data' in response and 'access_token' in response['data']:
        print(f"{Colors.OKGREEN}✅ Admin login successful!{Colors.ENDC}")
        return response['data']['access_token']
    else:
        print(f"{Colors.WARNING}⚠️  Admin login failed: {response}{Colors.ENDC}")
        return None

def ensure_tags_exist(admin_token: str) -> bool:
    """
    Ensure that the required tags exist in the system by checking if they can be used.
    This function tests if the tags exist by attempting to add them to a user.

    Args:
        admin_token: Admin token for administrative operations

    Returns:
        True if tags exist or can be used, False otherwise
    """
    print(f"{Colors.INFO}🔍 Checking if required tags exist in the system{Colors.ENDC}")

    # Test with a simple tag to see if the system is properly initialized
    test_tag = "0102"  # ADULT from AgeTag

    # Create a temporary test user to test tag functionality
    import time
    import random
    import string
    ts = int(time.time())
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_username = f"tag_test_{ts}_{random_suffix}"
    test_email = f"tag_test_{ts}_{random_suffix}@example.com"
    test_password = "SecurePassword123!"

    # Register test user
    register_url = f"{BASE_URL}/auth/register"
    register_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "first_name": "Tag",
        "last_name": "Test"
    }

    print(f"{Colors.INFO}📝 Creating temporary test user for tag validation{Colors.ENDC}")
    status_code, response = make_request(register_url, "POST", register_data)

    if status_code not in [200, 201]:
        print(f"{Colors.FAIL}❌ Failed to create test user for tag validation{Colors.ENDC}")
        return False

    user_id = response.get('data', {}).get('user_id')
    if not user_id:
        print(f"{Colors.FAIL}❌ Could not get user ID for tag validation{Colors.ENDC}")
        return False

    # Activate the test user
    activate_url = f"{BASE_URL}/admin/users/{user_id}"
    activate_data = {"is_active": True}
    headers = {"Authorization": f"Bearer {admin_token}"}

    status_code, response = make_request(activate_url, "PUT", activate_data, headers=headers)
    if status_code != 200:
        print(f"{Colors.FAIL}❌ Failed to activate test user{Colors.ENDC}")
        return False

    # Login as test user
    login_url = f"{BASE_URL}/auth/login"
    login_data = {"identifier": test_username, "password": test_password}
    status_code, response = make_request(login_url, "POST", login_data)

    if status_code != 200 or not response.get('data', {}).get('access_token'):
        print(f"{Colors.FAIL}❌ Failed to login test user{Colors.ENDC}")
        return False

    test_user_token = response['data']['access_token']

    # Try to add a test tag
    add_tags_url = f"{BASE_URL}/users/me/tags"
    add_tags_data = {"tag_values": [test_tag]}
    headers = {"Authorization": f"Bearer {test_user_token}"}

    print(f"{Colors.INFO}🧪 Testing tag functionality with tag: {test_tag}{Colors.ENDC}")
    status_code, response = make_request(add_tags_url, "POST", add_tags_data, headers=headers)

    print(f"{Colors.INFO}📥 Tag test response status: {status_code}{Colors.ENDC}")
    print(f"{Colors.INFO}📥 Tag test response data: {json.dumps(response, indent=2)}{Colors.ENDC}")

    # Clean up: delete test user
    delete_headers = {"Authorization": f"Bearer {admin_token}"}
    delete_status, delete_response = make_request(f"{BASE_URL}/admin/users/{user_id}", "DELETE", headers=delete_headers)
    print(f"{Colors.INFO}🧹 Cleaned up test user (status: {delete_status}){Colors.ENDC}")

    # If the tag was added successfully or if it already existed, the system is working
    if status_code in [200, 201]:
        print(f"{Colors.OKGREEN}✅ Tags system is working properly{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.WARNING}⚠️  Tags system may not be properly initialized{Colors.ENDC}")
        print(f"{Colors.WARNING}⚠️  Tag values may need to be pre-populated in the database{Colors.ENDC}")
        return False

def run_tags_test():
    """Run the complete user tags management flow test."""
    print(f"{Colors.HEADER}🧪 Testing User Tags Management Flow{Colors.ENDC}")
    print(f"{Colors.INFO}Gateway URL: {GATEWAY_URL}{Colors.ENDC}")

    # Generate unique test user credentials
    import time
    import random
    import string
    ts = int(time.time())
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_username = f"testuser_{ts}_{random_suffix}"
    test_email = f"testuser_{ts}_{random_suffix}@example.com"
    test_password = "SecurePassword123!"

    print(f"{Colors.INFO}Username: {test_username}{Colors.ENDC}")

    # Step 1: Register a new test user
    print(f"\n{Colors.BOLD}[1] REGISTER TEST USER{Colors.ENDC}")
    registration_success, user_id = register_user(test_username, test_email, test_password, "Test", "User")
    if not registration_success:
        print(f"{Colors.FAIL}❌ Cannot proceed without successful registration{Colors.ENDC}")
        sys.exit(1)

    # Step 2: Get admin token and activate the user
    print(f"\n{Colors.BOLD}[2] ACTIVATE USER ACCOUNT{Colors.ENDC}")
    admin_token = get_admin_token()
    if not admin_token:
        print(f"{Colors.FAIL}❌ Cannot proceed without admin token for activation{Colors.ENDC}")
        sys.exit(1)

    if user_id:
        activation_success = activate_user_with_admin(admin_token, user_id)
        if not activation_success:
            print(f"{Colors.FAIL}❌ Cannot proceed without activated user account{Colors.ENDC}")
            sys.exit(1)
    else:
        print(f"{Colors.WARNING}⚠️  Could not get user ID for activation, assuming user exists{Colors.ENDC}")

    # Step 3: Check if tags system is properly initialized
    print(f"\n{Colors.BOLD}[3] VALIDATE TAGS SYSTEM{Colors.ENDC}")
    tags_system_ok = ensure_tags_exist(admin_token)
    if not tags_system_ok:
        print(f"{Colors.WARNING}⚠️  Tags system may not be fully initialized{Colors.ENDC}")
        print(f"{Colors.WARNING}⚠️  The test will continue but tag operations may not work as expected{Colors.ENDC}")

    # Step 4: Login to get authentication token
    print(f"\n{Colors.BOLD}[4] LOGIN{Colors.ENDC}")
    auth_token = login_user(test_username, test_password)
    if not auth_token:
        print(f"{Colors.FAIL}❌ Cannot proceed without authentication token{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.OKGREEN}✅ Authentication token obtained{Colors.ENDC}")
    
    # Step 5: Get current user's tags
    print(f"\n{Colors.BOLD}[5] GET CURRENT USER TAGS{Colors.ENDC}")
    initial_tags = get_user_tags(auth_token)
    if initial_tags is None:
        print(f"{Colors.WARNING}⚠️  Could not retrieve initial tags, continuing anyway{Colors.ENDC}")
        initial_tags = {"data": {"age": [], "medical": [], "allergy": [], "diet": [], "taste": []}, "total_tags": 0, "categories_count": {}}

    # Step 6: Add some tags
    print(f"\n{Colors.BOLD}[6] ADD TAGS{Colors.ENDC}")
    tags_to_add = ["0102", "0212", "0302", "0402", "0501"]  # ADULT, DIABETES, DAIRY, VEGAN, SWEET_PREF
    add_result = add_user_tags(auth_token, tags_to_add)
    if not add_result:
        print(f"{Colors.FAIL}❌ Failed to add tags{Colors.ENDC}")
        sys.exit(1)

    # Step 7: Update tags in a specific category
    print(f"\n{Colors.BOLD}[7] UPDATE CATEGORY TAGS{Colors.ENDC}")
    category_to_update = "taste"
    new_taste_tags = ["0501", "0505", "0506"]  # SWEET_PREF, SPICY_PREF, LIGHT_PREF
    update_result = update_category_tags(auth_token, category_to_update, new_taste_tags)
    if not update_result:
        print(f"{Colors.FAIL}❌ Failed to update category tags{Colors.ENDC}")
        sys.exit(1)

    # Step 8: Get updated tags to verify changes
    print(f"\n{Colors.BOLD}[8] VERIFY CHANGES - GET UPDATED TAGS{Colors.ENDC}")
    updated_tags = get_user_tags(auth_token)
    if not updated_tags:
        print(f"{Colors.FAIL}❌ Failed to get updated tags{Colors.ENDC}")
        sys.exit(1)

    # Step 9: Delete some tags
    print(f"\n{Colors.BOLD}[9] DELETE TAGS{Colors.ENDC}")
    tags_to_delete = ["0212", "0302"]  # DIABETES, DAIRY
    delete_result = delete_user_tags(auth_token, tags_to_delete)
    if not delete_result:
        print(f"{Colors.FAIL}❌ Failed to delete tags{Colors.ENDC}")
        sys.exit(1)

    # Step 10: Final verification
    print(f"\n{Colors.BOLD}[10] FINAL VERIFICATION - GET FINAL TAGS{Colors.ENDC}")
    final_tags = get_user_tags(auth_token)
    if not final_tags:
        print(f"{Colors.FAIL}❌ Failed to get final tags{Colors.ENDC}")
        sys.exit(1)

    print(f"\n{Colors.OKGREEN}🎉 User Tags Management Flow completed successfully!{Colors.ENDC}")
    print(f"{Colors.INFO}Initial total tags: {initial_tags.get('total_tags', 0)}{Colors.ENDC}")
    print(f"{Colors.INFO}Final total tags: {final_tags.get('total_tags', 0)}{Colors.ENDC}")

    # Display final tag summary
    print(f"\n{Colors.BOLD}📊 FINAL TAG SUMMARY:{Colors.ENDC}")
    try:
        tags_data = final_tags.get('data', {}).get('data', {})
        has_tags = False
        for category, tags in tags_data.items():
            if tags:  # Only show categories that have tags
                has_tags = True
                print(f"  {category.upper()}: {len(tags)} tags")
                for tag in tags:
                    print(f"    - {tag['tag_name']} ({tag['tag_value']}): {tag['description'] or 'No description'}")

        if not has_tags:
            print(f"  No tags found for this user")
    except Exception as e:
        print(f"  Error displaying tag summary: {e}")

def main():
    """Main function to run the test."""
    try:
        run_tags_test()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Test interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Unexpected error during test: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()