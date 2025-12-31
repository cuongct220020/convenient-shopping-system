#!/usr/bin/env python3
"""
Comprehensive Test Script for Admin APIs using pytest.
Tests User Management endpoints: login, create user, update user info (core, identity, health profiles), delete user, activate user.
"""
import pytest
import pytest_asyncio
import time


class TestAdminUserManagementThroughGateway:
    """Test class for admin user management workflows through Kong Gateway"""

    def __init__(self):
        self.admin_token = None
        self.created_user_ids = []

    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def setup_method(self, test_client):
        """Setup method to initialize the test client and get admin token through Kong gateway"""
        # For testing through Kong gateway, we'll use HTTPX to make requests
        import httpx

        # Login as admin to get token through Kong gateway
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            login_response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": "admin",
                    "password": "admin"
                },
                headers={"Content-Type": "application/json"}
            )
            assert login_response.status_code == 200
            login_data = login_response.json()
            self.admin_token = login_data["data"]["access_token"]
            assert self.admin_token is not None
        
    async def cleanup_created_users(self):
        """Clean up all users created during tests"""
        import httpx
        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        for user_id in self.created_user_ids:
            try:
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    await client.delete(
                        f"/api/v1/user-service/admin/users/{user_id}",
                        headers=headers
                    )
            except:
                pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_admin_login_through_gateway(self):
        """Test admin login functionality through Kong gateway"""
        import httpx
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": "admin",
                    "password": "admin"
                },
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "access_token" in data["data"]
            assert data["data"]["access_token"] is not None

    @pytest.mark.asyncio
    async def test_create_user_through_gateway(self):
        """Test creating a new user as admin through Kong gateway"""
        import httpx
        timestamp = int(time.time())
        username = f"testuser_{timestamp}"
        email = f"test_{timestamp}@example.com"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        payload = {
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Test",
            "last_name": "User",
            "system_role": "user",
            "is_active": True,
            "phone_num": "1234567890"
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/user-service/admin/users",
                json=payload,
                headers=headers
            )

            assert response.status_code == 201
            data = response.json()
            assert "data" in data
            assert data["data"]["username"] == username
            assert data["data"]["email"] == email

            # Store user ID for cleanup
            user_id = data["data"]["id"]
            self.created_user_ids.append(user_id)
        
    @pytest.mark.asyncio
    async def test_update_core_user_info_through_gateway(self):
        """Test updating core user information through Kong gateway"""
        import httpx
        # First create a user
        timestamp = int(time.time())
        username = f"update_test_{timestamp}"
        email = f"update_{timestamp}@example.com"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        create_payload = {
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Original",
            "last_name": "User",
            "system_role": "user",
            "is_active": True,
            "phone_num": "1234567890"
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_response = await client.post(
                "/api/v1/user-service/admin/users",
                json=create_payload,
                headers=headers
            )

            assert create_response.status_code == 201
            create_data = create_response.json()
            user_id = create_data["data"]["id"]
            self.created_user_ids.append(user_id)

            # Update the user's core info
            update_payload = {
                "first_name": "Updated",
                "last_name": "Name",
                "phone_num": "0987654321",
                "email": f"updated_{timestamp}@example.com"
            }

            update_response = await client.patch(
                f"/api/v1/user-service/admin/users/{user_id}",
                json=update_payload,
                headers=headers
            )

            assert update_response.status_code == 200
            update_data = update_response.json()
            assert update_data["data"]["first_name"] == "Updated"
            assert update_data["data"]["last_name"] == "Name"
            assert update_data["data"]["phone_num"] == "0987654321"
            assert update_data["data"]["email"] == f"updated_{timestamp}@example.com"

    @pytest.mark.asyncio
    async def test_update_identity_profile_through_gateway(self):
        """Test updating identity profile information through Kong gateway"""
        import httpx
        # First create a user
        timestamp = int(time.time())
        username = f"identity_test_{timestamp}"
        email = f"identity_{timestamp}@example.com"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        create_payload = {
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Identity",
            "last_name": "Test",
            "system_role": "user",
            "is_active": True,
            "phone_num": "1234567890"
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_response = await client.post(
                "/api/v1/user-service/admin/users",
                json=create_payload,
                headers=headers
            )

            assert create_response.status_code == 201
            create_data = create_response.json()
            user_id = create_data["data"]["id"]
            self.created_user_ids.append(user_id)

            # Update identity profile
            identity_payload = {
                "identity_number": "ID123456789",
                "identity_issued_date": "2023-01-01",
                "identity_issued_place": "Hanoi",
                "date_of_birth": "1990-01-01",
                "gender": "male"
            }

            update_response = await client.patch(
                f"/api/v1/user-service/admin/users/{user_id}",
                json=identity_payload,
                headers=headers
            )

            assert update_response.status_code == 200
            update_data = update_response.json()

            # Verify identity profile fields are updated
            for key, value in identity_payload.items():
                assert update_data["data"][key] == value

    @pytest.mark.asyncio
    async def test_update_health_profile_through_gateway(self):
        """Test updating health profile information through Kong gateway"""
        import httpx
        # First create a user
        timestamp = int(time.time())
        username = f"health_test_{timestamp}"
        email = f"health_{timestamp}@example.com"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        create_payload = {
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Health",
            "last_name": "Test",
            "system_role": "user",
            "is_active": True,
            "phone_num": "1234567890"
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_response = await client.post(
                "/api/v1/user-service/admin/users",
                json=create_payload,
                headers=headers
            )

            assert create_response.status_code == 201
            create_data = create_response.json()
            user_id = create_data["data"]["id"]
            self.created_user_ids.append(user_id)

            # Update health profile
            health_payload = {
                "height": 175,
                "weight": 70,
                "blood_type": "O+",
                "allergies": "Peanuts",
                "chronic_diseases": "Diabetes",
                "current_medications": "Insulin"
            }

            update_response = await client.patch(
                f"/api/v1/user-service/admin/users/{user_id}",
                json=health_payload,
                headers=headers
            )

            assert update_response.status_code == 200
            update_data = update_response.json()

            # Verify health profile fields are updated
            for key, value in health_payload.items():
                assert update_data["data"][key] == value

    @pytest.mark.asyncio
    async def test_delete_user_through_gateway(self):
        """Test deleting a user as admin through Kong gateway"""
        import httpx
        # First create a user
        timestamp = int(time.time())
        username = f"delete_test_{timestamp}"
        email = f"delete_{timestamp}@example.com"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        create_payload = {
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Delete",
            "last_name": "Test",
            "system_role": "user",
            "is_active": True,
            "phone_num": "1234567890"
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_response = await client.post(
                "/api/v1/user-service/admin/users",
                json=create_payload,
                headers=headers
            )

            assert create_response.status_code == 201
            create_data = create_response.json()
            user_id = create_data["data"]["id"]

            # Delete the user
            delete_response = await client.delete(
                f"/api/v1/user-service/admin/users/{user_id}",
                headers=headers
            )

            assert delete_response.status_code == 200
            delete_data = delete_response.json()
            assert delete_data["message"] == "User deleted successfully"

            # Verify user is deleted by trying to get user details
            get_response = await client.get(
                f"/api/v1/user-service/admin/users/{user_id}",
                headers=headers
            )

            assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_activate_user_through_gateway(self):
        """Test activating a user through Kong gateway"""
        import httpx
        # First create an inactive user
        timestamp = int(time.time())
        username = f"inactive_test_{timestamp}"
        email = f"inactive_{timestamp}@example.com"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        create_payload = {
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Inactive",
            "last_name": "Test",
            "system_role": "user",
            "is_active": False,  # Create as inactive
            "phone_num": "1234567890"
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_response = await client.post(
                "/api/v1/user-service/admin/users",
                json=create_payload,
                headers=headers
            )

            assert create_response.status_code == 201
            create_data = create_response.json()
            user_id = create_data["data"]["id"]
            self.created_user_ids.append(user_id)

            # Verify user is initially inactive
            assert create_data["data"]["is_active"] is False

            # Activate the user
            activate_payload = {"is_active": True}
            activate_response = await client.patch(
                f"/api/v1/user-service/admin/users/{user_id}",
                json=activate_payload,
                headers=headers
            )

            assert activate_response.status_code == 200
            activate_data = activate_response.json()
            assert activate_data["data"]["is_active"] is True

            # Verify activation by getting user details
            get_response = await client.get(
                f"/api/v1/user-service/admin/users/{user_id}",
                headers=headers
            )

            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["data"]["is_active"] is True

    @pytest.mark.asyncio
    async def test_deactivate_user_through_gateway(self):
        """Test deactivating a user through Kong gateway"""
        import httpx
        # First create an active user
        timestamp = int(time.time())
        username = f"deactivate_test_{timestamp}"
        email = f"deactivate_{timestamp}@example.com"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        create_payload = {
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "first_name": "Active",
            "last_name": "Test",
            "system_role": "user",
            "is_active": True,  # Create as active
            "phone_num": "1234567890"
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            create_response = await client.post(
                "/api/v1/user-service/admin/users",
                json=create_payload,
                headers=headers
            )

            assert create_response.status_code == 201
            create_data = create_response.json()
            user_id = create_data["data"]["id"]
            self.created_user_ids.append(user_id)

            # Verify user is initially active
            assert create_data["data"]["is_active"] is True

            # Deactivate the user
            deactivate_payload = {"is_active": False}
            deactivate_response = await client.patch(
                f"/api/v1/user-service/admin/users/{user_id}",
                json=deactivate_payload,
                headers=headers
            )

            assert deactivate_response.status_code == 200
            deactivate_data = deactivate_response.json()
            assert deactivate_data["data"]["is_active"] is False

            # Verify deactivation by getting user details
            get_response = await client.get(
                f"/api/v1/user-service/admin/users/{user_id}",
                headers=headers
            )

            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["data"]["is_active"] is False

    @pytest.mark.asyncio
    async def test_full_user_management_workflow_through_gateway(self):
        """Test the complete user management workflow through Kong gateway: create -> update -> activate/deactivate -> delete"""
        import httpx
        timestamp = int(time.time())
        username = f"workflow_test_{timestamp}"
        email = f"workflow_{timestamp}@example.com"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # 1. Create user
            create_payload = {
                "username": username,
                "email": email,
                "password": "SecurePassword123!",
                "first_name": "Workflow",
                "last_name": "Test",
                "system_role": "user",
                "is_active": False,  # Start as inactive
                "phone_num": "1234567890"
            }

            create_response = await client.post(
                "/api/v1/user-service/admin/users",
                json=create_payload,
                headers=headers
            )

            assert create_response.status_code == 201
            create_data = create_response.json()
            user_id = create_data["data"]["id"]
            # Don't add to cleanup list here as we'll delete it in this test

            # Verify creation
            assert create_data["data"]["username"] == username
            assert create_data["data"]["email"] == email
            assert create_data["data"]["is_active"] is False

            # 2. Update core info
            update_core_payload = {
                "first_name": "UpdatedWorkflow",
                "last_name": "Tester",
                "phone_num": "0987654321"
            }

            update_core_response = await client.patch(
                f"/api/v1/user-service/admin/users/{user_id}",
                json=update_core_payload,
                headers=headers
            )

            assert update_core_response.status_code == 200
            update_core_data = update_core_response.json()
            assert update_core_data["data"]["first_name"] == "UpdatedWorkflow"
            assert update_core_data["data"]["last_name"] == "Tester"

            # 3. Update identity profile
            update_identity_payload = {
                "identity_number": "WF123456789",
                "identity_issued_date": "2023-06-01",
                "identity_issued_place": "Ho Chi Minh City",
                "date_of_birth": "1995-05-15",
                "gender": "female"
            }

            update_identity_response = await client.patch(
                f"/api/v1/user-service/admin/users/{user_id}",
                json=update_identity_payload,
                headers=headers
            )

            assert update_identity_response.status_code == 200
            update_identity_data = update_identity_response.json()
            for key, value in update_identity_payload.items():
                assert update_identity_data["data"][key] == value

            # 4. Update health profile
            update_health_payload = {
                "height": 165,
                "weight": 60,
                "blood_type": "A+",
                "allergies": "Dust",
                "chronic_diseases": "Asthma",
                "current_medications": "Inhaler"
            }

            update_health_response = await client.patch(
                f"/api/v1/user-service/admin/users/{user_id}",
                json=update_health_payload,
                headers=headers
            )

            assert update_health_response.status_code == 200
            update_health_data = update_health_response.json()
            for key, value in update_health_payload.items():
                assert update_health_data["data"][key] == value

            # 5. Activate user
            activate_payload = {"is_active": True}
            activate_response = await client.patch(
                f"/api/v1/user-service/admin/users/{user_id}",
                json=activate_payload,
                headers=headers
            )

            assert activate_response.status_code == 200
            activate_data = activate_response.json()
            assert activate_data["data"]["is_active"] is True

            # 6. Verify all changes
            get_response = await client.get(
                f"/api/v1/user-service/admin/users/{user_id}",
                headers=headers
            )

            assert get_response.status_code == 200
            final_data = get_response.json()["data"]
            assert final_data["username"] == username
            assert final_data["email"] == email
            assert final_data["first_name"] == "UpdatedWorkflow"
            assert final_data["last_name"] == "Tester"
            assert final_data["phone_num"] == "0987654321"
            assert final_data["identity_number"] == "WF123456789"
            assert final_data["height"] == 165
            assert final_data["is_active"] is True

            # 7. Delete user
            delete_response = await client.delete(
                f"/api/v1/user-service/admin/users/{user_id}",
                headers=headers
            )

            assert delete_response.status_code == 200
            delete_data = delete_response.json()
            assert delete_data["message"] == "User deleted successfully"

            # Verify user is deleted
            verify_delete_response = await client.get(
                f"/api/v1/user-service/admin/users/{user_id}",
                headers=headers
            )

            assert verify_delete_response.status_code == 404


    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def cleanup_method(self):
        """Cleanup method to clean up created users after each test"""
        yield  # This allows the test to run
        # Cleanup after test
        await self.cleanup_created_users()


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


class TestAdminGroupManagementThroughGateway:
    """Test class for admin group management workflows through Kong Gateway"""

    def __init__(self):
        self.admin_token = None
        self.created_user_ids = []
        self.created_group_ids = []

    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def setup_method(self):
        """Setup method to initialize the test client and get admin token through Kong gateway"""
        import httpx

        # Login as admin to get token through Kong gateway
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            login_response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": "admin",
                    "password": "admin"
                },
                headers={"Content-Type": "application/json"}
            )
            assert login_response.status_code == 200
            login_data = login_response.json()
            self.admin_token = login_data["data"]["access_token"]
            assert self.admin_token is not None

    async def cleanup_created_resources(self):
        """Clean up all users and groups created during tests"""
        import httpx
        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}

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
        for user_id in self.created_user_ids:
            try:
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    await client.delete(
                        f"/api/v1/user-service/admin/users/{user_id}",
                        headers=headers
                    )
            except:
                pass  # Ignore cleanup errors

    async def create_test_user(self, username_suffix=""):
        """Helper method to create a test user"""
        import httpx
        timestamp = int(time.time())
        username = f"testuser_{username_suffix}_{timestamp}"
        email = f"test_{username_suffix}_{timestamp}@example.com"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        payload = {
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "first_name": f"Test{username_suffix}",
            "last_name": "User",
            "system_role": "user",
            "is_active": True,
            "phone_num": "1234567890"
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/user-service/admin/users",
                json=payload,
                headers=headers
            )

            assert response.status_code == 201
            data = response.json()
            assert "data" in data
            assert data["data"]["username"] == username
            assert data["data"]["email"] == email

            # Store user ID for cleanup
            user_id = data["data"]["id"]
            self.created_user_ids.append(user_id)

            return user_id, username, email

    async def create_test_group(self, group_name_suffix=""):
        """Helper method to create a test group"""
        import httpx
        timestamp = int(time.time())
        group_name = f"Test Group {group_name_suffix} {timestamp}"

        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        payload = {
            "group_name": group_name
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/user-service/admin/groups",
                json=payload,
                headers=headers
            )

            assert response.status_code == 201
            data = response.json()
            assert "data" in data
            assert data["data"]["group_name"] == group_name

            # Store group ID for cleanup
            group_id = data["data"]["id"]
            self.created_group_ids.append(group_id)

            return group_id, group_name

    @pytest.mark.asyncio
    async def test_group_management_full_workflow(self):
        """Test the complete group management workflow: login -> create group -> create users -> add users to group -> assign headchef -> remove user from group"""
        import httpx
        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}

        # 1. Create a group
        group_id, group_name = await self.create_test_group("workflow")

        # 2. Create 2 users to add to the group
        user1_id, user1_username, user1_email = await self.create_test_user("group1")
        user2_id, user2_username, user2_email = await self.create_test_user("group2")

        # 3. Add users to the group
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Add first user to group
            add_user1_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": user1_email},
                headers=headers
            )
            assert add_user1_response.status_code == 201

            # Add second user to group
            add_user2_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": user2_email},
                headers=headers
            )
            assert add_user2_response.status_code == 201

            # Verify users were added by getting group details
            get_group_response = await client.get(
                f"/api/v1/user-service/admin/groups/{group_id}",
                headers=headers
            )
            assert get_group_response.status_code == 200
            group_data = get_group_response.json()["data"]
            members = group_data["members"]
            assert len(members) == 2
            member_emails = [member["user"]["email"] for member in members]
            assert user1_email in member_emails
            assert user2_email in member_emails

            # 4. Assign headchef role to one of the users
            assign_headchef_response = await client.patch(
                f"/api/v1/user-service/admin/groups/{group_id}/members/{user1_id}",
                json={"role": "head_chef"},
                headers=headers
            )
            assert assign_headchef_response.status_code == 200

            # Verify the role was assigned
            verify_role_response = await client.get(
                f"/api/v1/user-service/admin/groups/{group_id}",
                headers=headers
            )
            assert verify_role_response.status_code == 200
            updated_group_data = verify_role_response.json()["data"]
            user1_member = next((m for m in updated_group_data["members"] if m["user"]["id"] == user1_id), None)
            assert user1_member is not None
            assert user1_member["role"] == "head_chef"

            # 5. Remove one user from the group
            remove_user_response = await client.delete(
                f"/api/v1/user-service/admin/groups/{group_id}/members/{user2_id}",
                headers=headers
            )
            assert remove_user_response.status_code == 200

            # Verify the user was removed
            verify_removal_response = await client.get(
                f"/api/v1/user-service/admin/groups/{group_id}",
                headers=headers
            )
            assert verify_removal_response.status_code == 200
            final_group_data = verify_removal_response.json()["data"]
            final_members = final_group_data["members"]
            assert len(final_members) == 1
            assert final_members[0]["user"]["id"] == user1_id

    @pytest.mark.asyncio
    async def test_create_group_through_gateway(self):
        """Test creating a group as admin through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
        timestamp = int(time.time())
        group_name = f"Test Group {timestamp}"

        payload = {
            "group_name": group_name
        }

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post(
                "/api/v1/user-service/admin/groups",
                json=payload,
                headers=headers
            )

            assert response.status_code == 201
            data = response.json()
            assert "data" in data
            assert data["data"]["group_name"] == group_name

            # Store group ID for cleanup
            group_id = data["data"]["id"]
            self.created_group_ids.append(group_id)

    @pytest.mark.asyncio
    async def test_add_users_to_group_through_gateway(self):
        """Test adding users to a group as admin through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}

        # Create a group
        group_id, group_name = await self.create_test_group("add_users")

        # Create 2 users to add to the group
        user1_id, user1_username, user1_email = await self.create_test_user("add1")
        user2_id, user2_username, user2_email = await self.create_test_user("add2")

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Add first user to group
            add_user1_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": user1_email},
                headers=headers
            )
            assert add_user1_response.status_code == 201

            # Add second user to group
            add_user2_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": user2_email},
                headers=headers
            )
            assert add_user2_response.status_code == 201

            # Verify both users were added
            get_group_response = await client.get(
                f"/api/v1/user-service/admin/groups/{group_id}",
                headers=headers
            )
            assert get_group_response.status_code == 200
            group_data = get_group_response.json()["data"]
            members = group_data["members"]
            assert len(members) == 2
            member_emails = [member["user"]["email"] for member in members]
            assert user1_email in member_emails
            assert user2_email in member_emails

    @pytest.mark.asyncio
    async def test_assign_headchef_role_through_gateway(self):
        """Test assigning headchef role to a user in a group through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}

        # Create a group
        group_id, group_name = await self.create_test_group("headchef")

        # Create a user to assign as headchef
        user_id, username, email = await self.create_test_user("headchef")

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Add user to group first
            add_user_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": email},
                headers=headers
            )
            assert add_user_response.status_code == 201

            # Assign headchef role to the user
            assign_role_response = await client.patch(
                f"/api/v1/user-service/admin/groups/{group_id}/members/{user_id}",
                json={"role": "head_chef"},
                headers=headers
            )
            assert assign_role_response.status_code == 200

            # Verify the role was assigned
            get_group_response = await client.get(
                f"/api/v1/user-service/admin/groups/{group_id}",
                headers=headers
            )
            assert get_group_response.status_code == 200
            group_data = get_group_response.json()["data"]
            user_member = next((m for m in group_data["members"] if m["user"]["id"] == user_id), None)
            assert user_member is not None
            assert user_member["role"] == "head_chef"

    @pytest.mark.asyncio
    async def test_remove_user_from_group_through_gateway(self):
        """Test removing a user from a group as admin through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}

        # Create a group
        group_id, group_name = await self.create_test_group("remove")

        # Create a user to add and then remove from the group
        user_id, username, email = await self.create_test_user("remove")

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Add user to group first
            add_user_response = await client.post(
                f"/api/v1/user-service/admin/groups/{group_id}/members",
                json={"email": email},
                headers=headers
            )
            assert add_user_response.status_code == 201

            # Verify user was added
            get_group_before_removal = await client.get(
                f"/api/v1/user-service/admin/groups/{group_id}",
                headers=headers
            )
            assert get_group_before_removal.status_code == 200
            group_data_before = get_group_before_removal.json()["data"]
            assert len(group_data_before["members"]) == 1

            # Remove user from group
            remove_user_response = await client.delete(
                f"/api/v1/user-service/admin/groups/{group_id}/members/{user_id}",
                headers=headers
            )
            assert remove_user_response.status_code == 200

            # Verify user was removed
            get_group_after_removal = await client.get(
                f"/api/v1/user-service/admin/groups/{group_id}",
                headers=headers
            )
            assert get_group_after_removal.status_code == 200
            group_data_after = get_group_after_removal.json()["data"]
            assert len(group_data_after["members"]) == 0

    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def cleanup_method(self):
        """Cleanup method to clean up created users and groups after each test"""
        yield  # This allows the test to run
        # Cleanup after test
        await self.cleanup_created_resources()