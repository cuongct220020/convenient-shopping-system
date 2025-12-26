#!/usr/bin/env python3
"""
Comprehensive Script to Test User Registration, Login, and Group Management Flow.

This script demonstrates the complete user journey:
1. Register a new user account
2. Login successfully 
3. Create a new group
4. Add members to the group
5. Kick members from the group
6. Transfer group ownership (HEAD_CHEF role)
7. View group members
8. View individual member profiles
"""

import json
import ssl
import urllib.request
import urllib.error
import sys
import os
import random
import string
import time
import uuid

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
BASE_URL = f"{GATEWAY_URL}/api/v1/user-service"

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(msg):
    print(f"{Colors.HEADER}\n[STEP] {msg}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKBLUE}ℹ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

def print_fail(msg, detail=None):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")
    if detail:
        try:
            # Try to format JSON nicely
            if isinstance(detail, str):
                detail = json.loads(detail)
            print(f"{Colors.FAIL}  Detail: {json.dumps(detail, indent=2)}{Colors.ENDC}")
        except:
            print(f"{Colors.FAIL}  Detail: {detail}{Colors.ENDC}")

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
        print(f"{Colors.FAIL}Connection Error to {url}: {e}{Colors.ENDC}")
        return 0, None
    except Exception as e:
        print(f"{Colors.FAIL}Unexpected Error: {e}{Colors.ENDC}")
        return 0, None


class GroupManagementTester:
    def __init__(self):
        # Generate unique identifiers for this test run
        ts = int(time.time())
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        
        # Main user credentials
        self.main_username = f"main_user_{ts}_{random_suffix}"
        self.main_email = f"main_user_{ts}_{random_suffix}@example.com"
        self.main_password = "password123"
        self.main_token = None
        self.main_user_id = None
        
        # Test member credentials
        self.member_username = f"test_member_{ts}_{random_suffix}"
        self.member_email = f"test_member_{ts}_{random_suffix}@example.com"
        self.member_password = "password123"
        self.member_token = None
        self.member_user_id = None
        
        # Group details
        self.group_id = None
        self.group_name = f"Test Group {ts}"
        
        # For admin activation (if needed)
        self.admin_token = None

    def register_and_activate_user(self, username, email, password, first_name="Test", last_name="User"):
        """Register a new user and activate via admin (simulating OTP verification)."""
        print_info(f"Registering user: {email}")
        
        # Register the user
        status, reg_res = make_request(f"{BASE_URL}/auth/register", "POST", {
            "username": username,
            "email": email, 
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        })
        
        if status != 201:
            print_fail(f"Registration failed for {email}", reg_res)
            return False, None, None
            
        user_id = reg_res['data']['id']
        print_success(f"User {email} registered successfully (ID: {user_id})")
        
        # Login as admin to activate the user
        if not self.admin_token:
            print_info("Logging in as admin to activate user...")
            admin_status, admin_res = make_request(f"{BASE_URL}/auth/login", "POST", {
                "identifier": "admin",
                "password": "admin"
            })
            
            if admin_status != 200:
                print_fail("Admin login failed", admin_res)
                return False, None, None
                
            self.admin_token = admin_res['data']['access_token']
            print_success("Admin login successful")
        
        # Activate the user via admin API
        activate_headers = {"Authorization": f"Bearer {self.admin_token}"}
        activate_status, activate_res = make_request(
            f"{BASE_URL}/admin/users/{user_id}/activate", 
            "PATCH", 
            headers=activate_headers
        )
        
        if activate_status != 200:
            print_fail(f"User activation failed for {email}", activate_res)
            return False, None, None
            
        print_success(f"User {email} activated successfully")
        return True, user_id, None

    def login_user(self, email, password):
        """Login a user and return the access token."""
        print_info(f"Logging in user: {email}")
        
        status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", {
            "identifier": email,
            "password": password
        })
        
        if status != 200:
            print_fail(f"Login failed for {email}", login_res)
            return None
            
        token = login_res['data']['access_token']
        print_success(f"Login successful for {email}")
        return token

    def run_test(self):
        """Run the complete test flow."""
        print(f"{Colors.HEADER}🧪 Starting Group Management Flow Test{Colors.ENDC}")
        print(f"{Colors.INFO}Gateway URL: {GATEWAY_URL}{Colors.ENDC}")
        
        # Step 1: Register and login main user
        print_step("1. Register and Login Main User")
        success, self.main_user_id, _ = self.register_and_activate_user(
            self.main_username, self.main_email, self.main_password
        )
        if not success:
            return False
            
        self.main_token = self.login_user(self.main_email, self.main_password)
        if not self.main_token:
            return False
        
        # Step 2: Register and login test member
        print_step("2. Register and Login Test Member")
        success, self.member_user_id, _ = self.register_and_activate_user(
            self.member_username, self.member_email, self.member_password
        )
        if not success:
            return False
            
        self.member_token = self.login_user(self.member_email, self.member_password)
        if not self.member_token:
            return False
        
        # Step 3: Create a new group
        print_step("3. Create a New Group")
        if not self.create_group():
            return False
        
        # Step 4: Add member to the group
        print_step("4. Add Member to Group")
        if not self.add_member_to_group():
            return False
        
        # Step 5: View group members
        print_step("5. View Group Members")
        if not self.view_group_members():
            return False
        
        # Step 6: View individual member profile
        print_step("6. View Individual Member Profile")
        if not self.view_member_profile():
            return False
        
        # Step 7: Transfer group ownership (role change)
        print_step("7. Transfer Group Ownership (HEAD_CHEF role)")
        if not self.transfer_group_ownership():
            return False
        
        # Step 8: Kick member from group
        print_step("8. Kick Member from Group")
        if not self.kick_member_from_group():
            return False
        
        # Step 9: Create a new group with the member to test if they can still create groups
        print_step("9. Create New Group with Former Member")
        if not self.create_second_group():
            return False
        
        print(f"\n{Colors.OKGREEN}🎉 ALL TESTS PASSED! Group Management Flow Completed Successfully.{Colors.ENDC}")
        return True

    def create_group(self):
        """Create a new group with the main user."""
        headers = {"Authorization": f"Bearer {self.main_token}"}
        payload = {
            "group_name": self.group_name,
            "group_avatar_url": "https://example.com/group-avatar.jpg"
        }
        
        status, response = make_request(f"{BASE_URL}/groups", "POST", payload, headers)
        
        if status != 201:
            print_fail("Failed to create group", response)
            return False
        
        self.group_id = response['data']['id']
        print_success(f"Group created successfully! Group ID: {self.group_id}")
        print_info(f"Group Name: {response['data']['group_name']}")
        print_info(f"Creator: {response['data']['creator']['username']}")
        return True

    def add_member_to_group(self):
        """Add a member to the group."""
        if not self.group_id:
            print_fail("No group ID available")
            return False
            
        headers = {"Authorization": f"Bearer {self.main_token}"}
        payload = {
            "email": self.member_email
        }
        
        status, response = make_request(
            f"{BASE_URL}/groups/{self.group_id}/members", 
            "POST", 
            payload, 
            headers
        )
        
        if status != 201:
            print_fail("Failed to add member to group", response)
            return False
        
        print_success(f"Member {self.member_email} added to group successfully!")
        print_info(f"Added as role: {response['data']['role']}")
        return True

    def view_group_members(self):
        """View all members in the group."""
        if not self.group_id:
            print_fail("No group ID available")
            return False
            
        headers = {"Authorization": f"Bearer {self.main_token}"}
        
        status, response = make_request(
            f"{BASE_URL}/groups/{self.group_id}/members", 
            "GET", 
            None, 
            headers
        )
        
        if status != 200:
            print_fail("Failed to view group members", response)
            return False
        
        members = response['data']
        print_success(f"Retrieved {len(members)} members from group:")
        for member in members:
            print_info(f"  - {member['user']['username']} ({member['user']['email']}) - Role: {member['role']}")
        return True

    def view_member_profile(self):
        """View detailed profile of a group member."""
        if not self.group_id or not self.member_user_id:
            print_fail("Group ID or Member User ID not available")
            return False
            
        headers = {"Authorization": f"Bearer {self.main_token}"}
        
        # View identity profile
        status, response = make_request(
            f"{BASE_URL}/groups/{self.group_id}/members/{self.member_user_id}/identity-profile", 
            "GET", 
            None, 
            headers
        )
        
        if status != 200:
            print_fail("Failed to view member identity profile", response)
            return False
        
        print_success(f"Retrieved identity profile for member {self.member_email}:")
        profile_data = response['data']
        print_info(f"  Full Name: {profile_data.get('full_name', 'N/A')}")
        print_info(f"  Date of Birth: {profile_data.get('date_of_birth', 'N/A')}")
        print_info(f"  Gender: {profile_data.get('gender', 'N/A')}")
        print_info(f"  Phone: {profile_data.get('phone', 'N/A')}")
        
        # View health profile
        status, response = make_request(
            f"{BASE_URL}/groups/{self.group_id}/members/{self.member_user_id}/health-profile", 
            "GET", 
            None, 
            headers
        )
        
        if status != 200:
            print_warning("Could not retrieve health profile (might not exist yet)")
        else:
            print_success(f"Retrieved health profile for member {self.member_email}:")
            health_data = response['data']
            print_info(f"  Height: {health_data.get('height_cm', 'N/A')} cm")
            print_info(f"  Weight: {health_data.get('current_weight_kg', 'N/A')} kg")
            print_info(f"  Activity Level: {health_data.get('activity_level', 'N/A')}")
            print_info(f"  Health Goal: {health_data.get('health_goal', 'N/A')}")
        
        return True

    def transfer_group_ownership(self):
        """Transfer group ownership (HEAD_CHEF role) to another member."""
        if not self.group_id or not self.member_user_id:
            print_fail("Group ID or Member User ID not available")
            return False
            
        headers = {"Authorization": f"Bearer {self.main_token}"}
        payload = {
            "role": "head_chef"  # Transfer HEAD_CHEF role to the member
        }
        
        status, response = make_request(
            f"{BASE_URL}/groups/{self.group_id}/members/{self.member_user_id}", 
            "PATCH", 
            payload, 
            headers
        )
        
        if status != 200:
            print_fail("Failed to transfer group ownership", response)
            return False
        
        print_success(f"Successfully transferred HEAD_CHEF role to member {self.member_email}")
        print_info(f"New role: {response['data']['role']}")
        return True

    def kick_member_from_group(self):
        """Kick a member from the group."""
        if not self.group_id or not self.member_user_id:
            print_fail("Group ID or Member User ID not available")
            return False
            
        headers = {"Authorization": f"Bearer {self.main_token}"}
        
        status, response = make_request(
            f"{BASE_URL}/groups/{self.group_id}/members/{self.member_user_id}", 
            "DELETE", 
            None, 
            headers
        )
        
        if status != 200:
            print_fail("Failed to kick member from group", response)
            return False
        
        print_success(f"Successfully kicked member {self.member_email} from group")
        return True

    def create_second_group(self):
        """Have the former member create a new group to test their continued functionality."""
        # Login as the member again
        member_token = self.login_user(self.member_email, self.member_password)
        if not member_token:
            print_fail("Could not re-login as member")
            return False
            
        headers = {"Authorization": f"Bearer {member_token}"}
        payload = {
            "group_name": f"Second Test Group {int(time.time())}",
            "group_avatar_url": "https://example.com/second-group-avatar.jpg"
        }
        
        status, response = make_request(f"{BASE_URL}/groups", "POST", payload, headers)
        
        if status != 201:
            print_fail("Failed to create second group with former member", response)
            return False
        
        second_group_id = response['data']['id']
        print_success(f"Former member successfully created a new group! Group ID: {second_group_id}")
        return True


def main():
    print("=" * 80)
    print("🔐 User Registration, Login & Group Management Flow Test")
    print(f"   Gateway URL: {GATEWAY_URL}")
    print("=" * 80)
    
    tester = GroupManagementTester()
    
    success = tester.run_test()
    
    if success:
        print(f"\n{Colors.OKGREEN}🎉 ALL TESTS PASSED!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}The complete user journey was successful:{Colors.ENDC}")
        print(f"{Colors.OKGREEN}  ✓ User registration and activation{Colors.ENDC}")
        print(f"{Colors.OKGREEN}  ✓ User login{Colors.ENDC}")
        print(f"{Colors.OKGREEN}  ✓ Group creation{Colors.ENDC}")
        print(f"{Colors.OKGREEN}  ✓ Adding members to group{Colors.ENDC}")
        print(f"{Colors.OKGREEN}  ✓ Viewing group members{Colors.ENDC}")
        print(f"{Colors.OKGREEN}  ✓ Viewing individual member profiles{Colors.ENDC}")
        print(f"{Colors.OKGREEN}  ✓ Transferring group ownership{Colors.ENDC}")
        print(f"{Colors.OKGREEN}  ✓ Kicking members from group{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}❌ SOME TESTS FAILED!{Colors.ENDC}")
        sys.exit(1)
    
    print("=" * 80)
    print("✨ Group Management Flow Test Completed")
    print("=" * 80)


if __name__ == "__main__":
    main()