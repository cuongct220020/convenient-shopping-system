#!/usr/bin/env python3
"""
Comprehensive Test Script for User Group Management APIs using pytest.
Tests the complete user journey: register, verify, login, create group, add members, view profiles, kick members, transfer ownership, leave group.
"""
import pytest
import pytest_asyncio
import time
import uuid


class TestUserGroupManagementThroughGateway:
    """Test class for user group management workflows through Kong Gateway"""

    def __init__(self):
        self.main_user_token = None
        self.main_user_id = None
        self.main_username = None
        self.main_email = None
        self.member1_token = None
        self.member1_id = None
        self.member1_username = None
        self.member1_email = None
        self.member2_token = None
        self.member2_id = None
        self.member2_username = None
        self.member2_email = None
        self.group_id = None
        self.created_user_ids = []
        self.created_group_ids = []

    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def setup_method(self):
        """Setup method to initialize the test client and create test users through Kong gateway"""
        import httpx

        # Generate unique identifiers for this test run
        ts = int(time.time())
        random_suffix = str(uuid.uuid4())[:8]

        # Main user credentials
        self.main_username = f"main_user_{ts}_{random_suffix}"
        self.main_email = f"main_user_{ts}_{random_suffix}@example.com"
        self.main_password = "SecurePassword123!"

        # Test member 1 credentials
        self.member1_username = f"test_member1_{ts}_{random_suffix}"
        self.member1_email = f"test_member1_{ts}_{random_suffix}@example.com"
        self.member1_password = "SecurePassword123!"

        # Test member 2 credentials
        self.member2_username = f"test_member2_{ts}_{random_suffix}"
        self.member2_email = f"test_member2_{ts}_{random_suffix}@example.com"
        self.member2_password = "SecurePassword123!"

        # Register main user
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Register main user
            register_main_response = await client.post(
                "/api/v1/user-service/auth/register",
                json={
                    "username": self.main_username,
                    "email": self.main_email,
                    "password": self.main_password,
                    "first_name": "Main",
                    "last_name": "User",
                    "phone_num": "1234567890"
                },
                headers={"Content-Type": "application/json"}
            )
            assert register_main_response.status_code in [200, 201]
            register_main_data = register_main_response.json()
            assert "data" in register_main_data

            # Login main user to get token
            login_main_response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": self.main_username,
                    "password": self.main_password
                },
                headers={"Content-Type": "application/json"}
            )
            assert login_main_response.status_code == 200
            login_main_data = login_main_response.json()
            self.main_user_token = login_main_data["data"]["access_token"]
            self.main_user_id = login_main_data["data"]["user"]["id"]
            assert self.main_user_token is not None
            assert self.main_user_id is not None

            # Register member 1
            register_member1_response = await client.post(
                "/api/v1/user-service/auth/register",
                json={
                    "username": self.member1_username,
                    "email": self.member1_email,
                    "password": self.member1_password,
                    "first_name": "Member",
                    "last_name": "One",
                    "phone_num": "1234567891"
                },
                headers={"Content-Type": "application/json"}
            )
            assert register_member1_response.status_code in [200, 201]
            register_member1_data = register_member1_response.json()
            assert "data" in register_member1_data

            # Login member 1 to get token
            login_member1_response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": self.member1_username,
                    "password": self.member1_password
                },
                headers={"Content-Type": "application/json"}
            )
            assert login_member1_response.status_code == 200
            login_member1_data = login_member1_response.json()
            self.member1_token = login_member1_data["data"]["access_token"]
            self.member1_id = login_member1_data["data"]["user"]["id"]
            assert self.member1_token is not None
            assert self.member1_id is not None

            # Register member 2
            register_member2_response = await client.post(
                "/api/v1/user-service/auth/register",
                json={
                    "username": self.member2_username,
                    "email": self.member2_email,
                    "password": self.member2_password,
                    "first_name": "Member",
                    "last_name": "Two",
                    "phone_num": "1234567892"
                },
                headers={"Content-Type": "application/json"}
            )
            assert register_member2_response.status_code in [200, 201]
            register_member2_data = register_member2_response.json()
            assert "data" in register_member2_data

            # Login member 2 to get token
            login_member2_response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": self.member2_username,
                    "password": self.member2_password
                },
                headers={"Content-Type": "application/json"}
            )
            assert login_member2_response.status_code == 200
            login_member2_data = login_member2_response.json()
            self.member2_token = login_member2_data["data"]["access_token"]
            self.member2_id = login_member2_data["data"]["user"]["id"]
            assert self.member2_token is not None
            assert self.member2_id is not None

    async def cleanup_created_resources(self):
        """Clean up all users and groups created during tests"""
        import httpx
        headers = {"Authorization": f"Bearer {self.main_user_token}", "Content-Type": "application/json"}
        
        # Clean up groups first
        for group_id in self.created_group_ids:
            try:
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    await client.delete(
                        f"/api/v1/user-service/admin/groups/{group_id}",
                        headers=headers
                    )
            except:
                pass  # Ignore cleanup errors

        # Clean up users
        admin_headers = {"Authorization": f"Bearer {self.get_admin_token()}", "Content-Type": "application/json"}
        for user_id in self.created_user_ids:
            try:
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    await client.delete(
                        f"/api/v1/user-service/admin/users/{user_id}",
                        headers=admin_headers
                    )
            except:
                pass  # Ignore cleanup errors

    def get_admin_token(self):
        """Get admin token for cleanup operations"""
        import httpx
        import asyncio
        
        async def get_token():
            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                login_response = await client.post(
                    "/api/v1/user-service/auth/login",
                    json={
                        "identifier": "admin",
                        "password": "admin"
                    },
                    headers={"Content-Type": "application/json"}
                )
                if login_response.status_code == 200:
                    return login_response.json()["data"]["access_token"]
                return None
        
        # Run the async function synchronously
        import subprocess
        import sys
        import threading
        import queue
        
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(get_token())
            q.put(result)
            loop.close()
        
        q = queue.Queue()
        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join()
        return q.get()

    @pytest.mark.asyncio
    async def test_complete_group_management_workflow(self):
        """Test the complete group management workflow: register -> login -> create group -> add members -> view profiles -> kick member -> transfer ownership -> leave group"""
        import httpx
        headers = {"Authorization": f"Bearer {self.main_user_token}", "Content-Type": "application/json"}

        # 1. Create a new group (main user is HEAD_CHEF by default)
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_group_response = await client.post(
                "/api/v1/user-service/groups",
                json={
                    "group_name": f"Test Group {int(time.time())}"
                },
                headers=headers
            )
            assert create_group_response.status_code == 201
            create_group_data = create_group_response.json()
            assert "data" in create_group_data
            self.group_id = create_group_data["data"]["id"]
            self.created_group_ids.append(self.group_id)
            assert create_group_data["data"]["group_name"] == f"Test Group {int(time.time())}"

        # 2. Add member 1 to the group
        add_member1_response = await client.post(
            f"/api/v1/user-service/admin/groups/{self.group_id}/members",
            json={"email": self.member1_email},
            headers=headers
        )
        assert add_member1_response.status_code == 201

        # 3. Add member 2 to the group
        add_member2_response = await client.post(
            f"/api/v1/user-service/admin/groups/{self.group_id}/members",
            json={"email": self.member2_email},
            headers=headers
        )
        assert add_member2_response.status_code == 201

        # 4. Verify members were added by getting group details
        get_group_response = await client.get(
            f"/api/v1/user-service/groups/{self.group_id}",
            headers=headers
        )
        assert get_group_response.status_code == 200
        group_data = get_group_response.json()["data"]
        members = group_data["members"]
        assert len(members) == 3  # Main user + 2 members
        member_emails = [member["user"]["email"] for member in members]
        assert self.main_email in member_emails
        assert self.member1_email in member_emails
        assert self.member2_email in member_emails

        # 5. View member profiles
        # Get member 1's identity profile
        get_member1_identity_response = await client.get(
            f"/api/v1/user-service/groups/{self.group_id}/members/{self.member1_id}/identity",
            headers=headers
        )
        assert get_member1_identity_response.status_code == 200

        # Get member 1's health profile
        get_member1_health_response = await client.get(
            f"/api/v1/user-service/groups/{self.group_id}/members/{self.member1_id}/health",
            headers=headers
        )
        assert get_member1_health_response.status_code == 200

        # 6. Transfer head_chef role to member 1
        transfer_role_response = await client.patch(
            f"/api/v1/user-service/admin/groups/{self.group_id}/members/{self.member1_id}",
            json={"role": "head_chef"},
            headers=headers
        )
        assert transfer_role_response.status_code == 200

        # Verify the role was transferred
        verify_role_response = await client.get(
            f"/api/v1/user-service/groups/{self.group_id}",
            headers=headers
        )
        assert verify_role_response.status_code == 200
        updated_group_data = verify_role_response.json()["data"]
        member1_member = next((m for m in updated_group_data["members"] if m["user"]["id"] == self.member1_id), None)
        assert member1_member is not None
        assert member1_member["role"] == "head_chef"

        # 7. Kick member 2 from the group (as the new head_chef)
        # First, get new token for member1 who is now head_chef
        new_headers = {"Authorization": f"Bearer {self.member1_token}", "Content-Type": "application/json"}
        
        kick_member_response = await client.delete(
            f"/api/v1/user-service/admin/groups/{self.group_id}/members/{self.member2_id}",
            headers=new_headers
        )
        assert kick_member_response.status_code == 200

        # Verify member 2 was removed
        verify_removal_response = await client.get(
            f"/api/v1/user-service/groups/{self.group_id}",
            headers=new_headers
        )
        assert verify_removal_response.status_code == 200
        final_group_data = verify_removal_response.json()["data"]
        final_members = final_group_data["members"]
        assert len(final_members) == 2  # Only main user and member 1 remain
        final_member_ids = [m["user"]["id"] for m in final_members]
        assert self.member2_id not in final_member_ids

    @pytest.mark.asyncio
    async def test_user_register_and_login_through_gateway(self):
        """Test user registration and login functionality through Kong gateway"""
        import httpx
        ts = int(time.time())
        random_suffix = str(uuid.uuid4())[:8]
        username = f"test_reg_login_{ts}_{random_suffix}"
        email = f"test_reg_login_{ts}_{random_suffix}@example.com"
        password = "SecurePassword123!"

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Register user
            register_response = await client.post(
                "/api/v1/user-service/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "first_name": "Test",
                    "last_name": "User",
                    "phone_num": "1234567890"
                },
                headers={"Content-Type": "application/json"}
            )
            assert register_response.status_code in [200, 201]
            register_data = register_response.json()
            assert "data" in register_data

            # Login user
            login_response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": username,
                    "password": password
                },
                headers={"Content-Type": "application/json"}
            )
            assert login_response.status_code == 200
            login_data = login_response.json()
            assert "data" in login_data
            assert "access_token" in login_data["data"]
            assert login_data["data"]["access_token"] is not None

    @pytest.mark.asyncio
    async def test_create_group_through_gateway(self):
        """Test creating a group as a regular user through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.main_user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_group_response = await client.post(
                "/api/v1/user-service/groups",
                json={
                    "group_name": f"Test Group {int(time.time())}"
                },
                headers=headers
            )
            assert create_group_response.status_code == 201
            create_group_data = create_group_response.json()
            assert "data" in create_group_data
            group_id = create_group_data["data"]["id"]
            self.created_group_ids.append(group_id)
            assert create_group_data["data"]["group_name"] == f"Test Group {int(time.time())}"

    @pytest.mark.asyncio
    async def test_add_members_to_group_through_gateway(self):
        """Test adding members to a group through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.main_user_token}", "Content-Type": "application/json"}

        # Create a group first
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_group_response = await client.post(
                "/api/v1/user-service/groups",
                json={
                    "group_name": f"Test Group {int(time.time())}"
                },
                headers=headers
            )
            assert create_group_response.status_code == 201
            create_group_data = create_group_response.json()
            assert "data" in create_group_data
            group_id = create_group_data["data"]["id"]
            self.created_group_ids.append(group_id)

            # Add member 1 to the group
            add_member_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": self.member1_email},
                headers=headers
            )
            assert add_member_response.status_code == 201

            # Verify member was added
            get_group_response = await client.get(
                f"/api/v1/user-service/groups/{group_id}",
                headers=headers
            )
            assert get_group_response.status_code == 200
            group_data = get_group_response.json()["data"]
            members = group_data["members"]
            assert len(members) == 2  # Main user + 1 member
            member_emails = [member["user"]["email"] for member in members]
            assert self.member1_email in member_emails

    @pytest.mark.asyncio
    async def test_view_member_profiles_through_gateway(self):
        """Test viewing member profiles through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.main_user_token}", "Content-Type": "application/json"}

        # Create a group and add a member first
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_group_response = await client.post(
                "/api/v1/user-service/groups",
                json={
                    "group_name": f"Test Group {int(time.time())}"
                },
                headers=headers
            )
            assert create_group_response.status_code == 201
            create_group_data = create_group_response.json()
            assert "data" in create_group_data
            group_id = create_group_data["data"]["id"]
            self.created_group_ids.append(group_id)

            # Add member to the group
            add_member_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": self.member1_email},
                headers=headers
            )
            assert add_member_response.status_code == 201

            # View member's identity profile
            get_identity_response = await client.get(
                f"/api/v1/user-service/groups/{group_id}/members/{self.member1_id}/identity",
                headers=headers
            )
            assert get_identity_response.status_code == 200
            identity_data = get_identity_response.json()
            assert "data" in identity_data

            # View member's health profile
            get_health_response = await client.get(
                f"/api/v1/user-service/groups/{group_id}/members/{self.member1_id}/health",
                headers=headers
            )
            assert get_health_response.status_code == 200
            health_data = get_health_response.json()
            assert "data" in health_data

    @pytest.mark.asyncio
    async def test_kick_user_from_group_through_gateway(self):
        """Test kicking a user from a group through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.main_user_token}", "Content-Type": "application/json"}

        # Create a group and add a member first
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_group_response = await client.post(
                "/api/v1/user-service/groups",
                json={
                    "group_name": f"Test Group {int(time.time())}"
                },
                headers=headers
            )
            assert create_group_response.status_code == 201
            create_group_data = create_group_response.json()
            assert "data" in create_group_data
            group_id = create_group_data["data"]["id"]
            self.created_group_ids.append(group_id)

            # Add member to the group
            add_member_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": self.member1_email},
                headers=headers
            )
            assert add_member_response.status_code == 201

            # Verify member was added
            get_group_before_kick = await client.get(
                f"/api/v1/user-service/groups/{group_id}",
                headers=headers
            )
            assert get_group_before_kick.status_code == 200
            group_data_before = get_group_before_kick.json()["data"]
            assert len(group_data_before["members"]) == 2

            # Kick the member from the group
            kick_member_response = await client.delete(
                f"/api/v1/user-service/admin/groups/{group_id}/members/{self.member1_id}",
                headers=headers
            )
            assert kick_member_response.status_code == 200

            # Verify member was removed
            get_group_after_kick = await client.get(
                f"/api/v1/user-service/groups/{group_id}",
                headers=headers
            )
            assert get_group_after_kick.status_code == 200
            group_data_after = get_group_after_kick.json()["data"]
            assert len(group_data_after["members"]) == 1
            assert group_data_after["members"][0]["user"]["id"] == self.main_user_id

    @pytest.mark.asyncio
    async def test_transfer_head_chef_role_through_gateway(self):
        """Test transferring head_chef role to another user through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.main_user_token}", "Content-Type": "application/json"}

        # Create a group and add a member first
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_group_response = await client.post(
                "/api/v1/user-service/groups",
                json={
                    "group_name": f"Test Group {int(time.time())}"
                },
                headers=headers
            )
            assert create_group_response.status_code == 201
            create_group_data = create_group_response.json()
            assert "data" in create_group_data
            group_id = create_group_data["data"]["id"]
            self.created_group_ids.append(group_id)

            # Add member to the group
            add_member_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": self.member1_email},
                headers=headers
            )
            assert add_member_response.status_code == 201

            # Verify initial roles
            get_group_before_transfer = await client.get(
                f"/api/v1/user-service/groups/{group_id}",
                headers=headers
            )
            assert get_group_before_transfer.status_code == 200
            group_data_before = get_group_before_transfer.json()["data"]
            main_member = next((m for m in group_data_before["members"] if m["user"]["id"] == self.main_user_id), None)
            assert main_member is not None
            assert main_member["role"] == "head_chef"  # Main user should be head_chef initially

            # Transfer head_chef role to the member
            transfer_role_response = await client.patch(
                f"/api/v1/user-service/admin/groups/{group_id}/members/{self.member1_id}",
                json={"role": "head_chef"},
                headers=headers
            )
            assert transfer_role_response.status_code == 200

            # Verify the role was transferred
            get_group_after_transfer = await client.get(
                f"/api/v1/user-service/groups/{group_id}",
                headers=headers
            )
            assert get_group_after_transfer.status_code == 200
            group_data_after = get_group_after_transfer.json()["data"]
            member_member = next((m for m in group_data_after["members"] if m["user"]["id"] == self.member1_id), None)
            main_member_after = next((m for m in group_data_after["members"] if m["user"]["id"] == self.main_user_id), None)
            assert member_member is not None
            assert member_member["role"] == "head_chef"
            assert main_member_after is not None
            assert main_member_after["role"] == "member"  # Main user should now be a regular member

    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def cleanup_method(self):
        """Cleanup method to clean up created users and groups after each test"""
        yield  # This allows the test to run
        # Cleanup after test
        await self.cleanup_created_resources()


# Test class to verify Kong gateway is working properly
class TestKongGatewayHealth:
    """Test class to verify Kong gateway is working properly"""

    @pytest.mark.asyncio
    async def test_kong_gateway_health(self):
        """Test that Kong gateway is accessible and responding"""
        import httpx

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Test that Kong gateway is running by making a request to a non-existent endpoint
            # This should return a 404 from Kong, not a connection error
            try:
                response = await client.get("/non-existent-endpoint")
                # If we get a response (even 404), it means Kong is running
                assert response.status_code in [404, 200, 405]  # Kong might return various codes
                print(f"Kong gateway is accessible. Status: {response.status_code}")
            except httpx.ConnectError:
                pytest.fail("Cannot connect to Kong gateway. Please ensure Kong is running on localhost:8000")