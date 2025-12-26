#!/usr/bin/env python3
"""
Comprehensive Test Script for Admin APIs.
Tests User Management and Group Management endpoints.
"""
import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/v1/user-service"
AUTH_URL = f"{BASE_URL}/auth"
ADMIN_USER_URL = f"{BASE_URL}/admin/users"
ADMIN_GROUP_URL = f"{BASE_URL}/admin/groups"
USER_GROUP_URL = f"{BASE_URL}/groups"

# ANSI Colors
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

def print_fail(msg, detail=None):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")
    if detail:
        print(f"{Colors.FAIL}  Detail: {detail}{Colors.ENDC}")
    # Don't exit immediately to allow cleanup if possible, 
    # but in a real test suite we might raise assertion error.

class AdminTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.created_users = [] # List of IDs to cleanup
        self.created_groups = [] # List of IDs to cleanup

    def login(self, username, password):
        print(f"Logging in as {username}...")
        resp = requests.post(f"{AUTH_URL}/login", json={
            "identifier": username,
            "password": password
        })
        if resp.status_code == 200:
            token = resp.json()['data']['access_token']
            print_success("Login successful")
            return token
        else:
            print_fail("Login failed", resp.text)
            return None

    def create_user_as_admin(self, username, email, password, role="user", phone="1234567890"):
        print(f"Creating user {username} ({role})...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "first_name": "Test",
            "last_name": "User",
            "system_role": role.lower(),
            "is_active": True,
            "phone_num": phone
        }
        resp = requests.post(ADMIN_USER_URL, json=payload, headers=headers)
        if resp.status_code == 201:
            user_data = resp.json()['data']
            print_success(f"User created: ID={user_data['id']}")
            self.created_users.append(user_data['id'])
            return user_data
        else:
            print_fail("Failed to create user", resp.text)
            return None

    def get_user_details(self, user_id):
        print(f"Getting details for user {user_id}...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.get(f"{ADMIN_USER_URL}/{user_id}", headers=headers)
        if resp.status_code == 200:
            print_success("Got user details")
            return resp.json()['data']
        else:
            print_fail("Failed to get user details", resp.text)
            return None

    def update_user(self, user_id, new_data):
        print(f"Updating user {user_id}...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.patch(f"{ADMIN_USER_URL}/{user_id}", json=new_data, headers=headers)
        if resp.status_code == 200:
            print_success("User updated")
            return resp.json()['data']
        else:
            print_fail("Failed to update user", resp.text)
            return None

    def delete_user(self, user_id):
        print(f"Deleting user {user_id}...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.delete(f"{ADMIN_USER_URL}/{user_id}", headers=headers)
        if resp.status_code == 200:
            print_success("User deleted")
        else:
            print_fail("Failed to delete user", resp.text)

    # --- Group Utils ---
    def create_group_as_user(self, token, name):
        print(f"Creating group '{name}' as user...")
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"group_name": name}
        resp = requests.post(USER_GROUP_URL, json=payload, headers=headers)
        if resp.status_code == 201:
            group_data = resp.json()['data']
            print_success(f"Group created: ID={group_data['id']}")
            self.created_groups.append(group_data['id'])
            return group_data
        else:
            print_fail("Failed to create group", resp.text)
            return None

    def get_admin_groups(self):
        print("Listing all groups as admin...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.get(ADMIN_GROUP_URL, headers=headers)
        if resp.status_code == 200:
            print_success("Got groups list")
            return resp.json()['data']
        else:
            print_fail("Failed to list groups", resp.text)
            return []

    def get_admin_group_detail(self, group_id):
        print(f"Getting group details {group_id} as admin...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.get(f"{ADMIN_GROUP_URL}/{group_id}", headers=headers)
        if resp.status_code == 200:
            print_success("Got group details")
            return resp.json()['data']
        else:
            print_fail("Failed to get group details", resp.text)
            return None

    def update_group_as_admin(self, group_id, name):
        print(f"Updating group {group_id} as admin...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.patch(f"{ADMIN_GROUP_URL}/{group_id}", json={"group_name": name}, headers=headers)
        if resp.status_code == 200:
            print_success("Group updated")
            return resp.json()['data']
        else:
            print_fail("Failed to update group", resp.text)
            return None

    def delete_group_as_admin(self, group_id):
        print(f"Deleting group {group_id} as admin...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.delete(f"{ADMIN_GROUP_URL}/{group_id}", headers=headers)
        if resp.status_code == 200:
            print_success("Group deleted")
        else:
            print_fail("Failed to delete group", resp.text)

    def add_member_as_admin(self, group_id, email):
        print(f"Adding member {email} to group {group_id} as admin...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.post(f"{ADMIN_GROUP_URL}/{group_id}/members", json={"email": email}, headers=headers)
        if resp.status_code == 201:
            print_success("Member added")
            return True
        else:
            print_fail("Failed to add member", resp.text)
            return False

    def update_member_role_as_admin(self, group_id, user_id, role):
        print(f"Updating member {user_id} role to {role}...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.patch(f"{ADMIN_GROUP_URL}/{group_id}/members/{user_id}", json={"role": role}, headers=headers)
        if resp.status_code == 200:
            print_success("Member role updated")
        else:
            print_fail("Failed to update member role", resp.text)

    def remove_member_as_admin(self, group_id, user_id):
        print(f"Removing member {user_id} from group {group_id}...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        resp = requests.delete(f"{ADMIN_GROUP_URL}/{group_id}/members/{user_id}", headers=headers)
        if resp.status_code == 200:
            print_success("Member removed")
        else:
            print_fail("Failed to remove member", resp.text)

    def run(self):
        print("🚀 Starting Admin API Tests")
        ts = int(time.time())
        u1_name = f"testuser1_{ts}"
        u1_email = f"u1_{ts}@example.com"
        u1_phone = f"091{ts}"
        
        u2_name = f"testuser2_{ts}"
        u2_email = f"u2_{ts}@example.com"
        u2_phone = f"092{ts}"
        
        # 1. Admin Login
        print_step("Admin Login")
        self.admin_token = self.login("admin", "admin")
        if not self.admin_token:
            return

        # 2. User Management Flow
        print_step("User Management Tests")
        user1 = self.create_user_as_admin(u1_name, u1_email, "password123", phone=u1_phone)
        if user1:
            self.get_user_details(user1['id'])
            self.update_user(user1['id'], {"first_name": "UpdatedName"})
            
            # Verify update
            u = self.get_user_details(user1['id'])
            if u and u['first_name'] == "UpdatedName":
                print_success("User update verified")
            else:
                print_fail("User update verification failed")

        # 3. Group Management Setup
        print_step("Group Management Setup")
        # Login as user1 to create a group
        user1_token = self.login(u1_name, "password123")
        group_id = None
        if user1_token:
            g = self.create_group_as_user(user1_token, f"Test Group {ts}")
            if g:
                group_id = g['id']

        # Create another user to be a member
        user2 = self.create_user_as_admin(u2_name, u2_email, "password123", phone=u2_phone)
        
        # 4. Group Management Admin Flow
        if group_id and user2:
            print_step("Group Admin Tests")
            
            # List groups
            groups_response = self.get_admin_groups()
            # The API returns GenericResponse(data=[...]) or PaginationResponse(data=[...])
            items = groups_response # self.get_admin_groups already returns resp.json()['data']
            
            print(f"Checking if group {group_id} is in {len(items)} items...")
            found = False
            for g in items:
                if str(g['id']) == str(group_id):
                    found = True
                    break
                    
            if found:
                print_success(f"Group {group_id} found in admin list")
            else:
                print_fail(f"Group {group_id} NOT found in admin list")

            # Get detail
            self.get_admin_group_detail(group_id)

            # Update group
            self.update_group_as_admin(group_id, f"Admin Renamed Group {ts}")
            
            # Add member
            self.add_member_as_admin(group_id, u2_email)
            
            # Verify member added (by checking details)
            g_detail = self.get_admin_group_detail(group_id)
            if g_detail:
                members = g_detail.get('members', [])
                m_found = any(str(m['user']['id']) == str(user2['id']) for m in members)
                if m_found:
                    print_success("Member found in group")
                else:
                    print_fail("Member NOT found in group")

            # Update member role
            self.update_member_role_as_admin(group_id, user2['id'], "head_chef")

            # Remove member
            self.remove_member_as_admin(group_id, user2['id'])
            
            # Delete Group
            self.delete_group_as_admin(group_id)
            # Remove from local cleanup list since it's deleted
            if group_id in self.created_groups:
                self.created_groups.remove(group_id)

if __name__ == "__main__":
    tester = AdminTester()
    tester.run()
