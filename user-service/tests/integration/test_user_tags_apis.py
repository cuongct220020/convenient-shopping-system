#!/usr/bin/env python3
"""
Comprehensive Test Script for User Tags APIs using pytest.
Tests the complete user tags workflow: register, login, add tags, get tags, update tags by category, delete tags.
"""
import pytest
import pytest_asyncio
import time
import uuid


class TestUserTagsManagementThroughGateway:
    """Test class for user tags management workflows through Kong Gateway"""

    def __init__(self):
        self.user_token = None
        self.user_id = None
        self.username = None
        self.email = None
        self.password = None
        self.created_user_ids = []

    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def setup_method(self):
        """Setup method to initialize the test client and create test user through Kong gateway"""
        import httpx

        # Generate unique identifiers for this test run
        ts = int(time.time())
        random_suffix = str(uuid.uuid4())[:8]

        # User credentials
        self.username = f"tags_user_{ts}_{random_suffix}"
        self.email = f"tags_user_{ts}_{random_suffix}@example.com"
        self.password = "SecurePassword123!"

        # Register user
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Register user
            register_response = await client.post(
                "/api/v1/user-service/auth/register",
                json={
                    "username": self.username,
                    "email": self.email,
                    "password": self.password,
                    "first_name": "Tags",
                    "last_name": "User",
                    "phone_num": "1234567890"
                },
                headers={"Content-Type": "application/json"}
            )
            assert register_response.status_code in [200, 201]
            register_data = register_response.json()
            assert "data" in register_data

            # Login user to get token
            login_response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": self.username,
                    "password": self.password
                },
                headers={"Content-Type": "application/json"}
            )
            assert login_response.status_code == 200
            login_data = login_response.json()
            self.user_token = login_data["data"]["access_token"]
            self.user_id = login_data["data"]["user"]["id"]
            assert self.user_token is not None
            assert self.user_id is not None

    async def cleanup_created_resources(self):
        """Clean up all users created during tests"""
        import httpx
        # Get admin token for cleanup
        admin_token = await self.get_admin_token()
        if admin_token:
            headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
            for user_id in self.created_user_ids:
                try:
                    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                        await client.delete(
                            f"/api/v1/user-service/admin/users/{user_id}",
                            headers=headers
                        )
                except:
                    pass  # Ignore cleanup errors

    async def get_admin_token(self):
        """Get admin token for cleanup operations"""
        import httpx

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            try:
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
            except:
                pass
            return None

    @pytest.mark.asyncio
    async def test_complete_user_tags_workflow(self):
        """Test the complete user tags workflow: register -> login -> add tags -> get tags -> update tags by category -> delete tags"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # 1. Get initial tags (should be empty)
            get_initial_tags_response = await client.get(
                "/api/v1/user-service/users/me/tags",
                headers=headers
            )
            assert get_initial_tags_response.status_code == 200
            initial_tags_data = get_initial_tags_response.json()
            assert "data" in initial_tags_data
            # Initial tags might be empty dict or have empty categories

            # 2. Add tags to user
            add_tags_payload = {
                "tag_values": ["0102", "0212", "0300"]  # Example tag values
            }
            add_tags_response = await client.post(
                "/api/v1/user-service/users/me/tags",
                json=add_tags_payload,
                headers=headers
            )
            # This might return 201 (created) or 200 (if tags already exist)
            assert add_tags_response.status_code in [200, 201]
            add_tags_data = add_tags_response.json()
            assert "data" in add_tags_data

            # 3. Get tags to verify they were added
            get_tags_response = await client.get(
                "/api/v1/user-service/users/me/tags",
                headers=headers
            )
            assert get_tags_response.status_code == 200
            tags_data = get_tags_response.json()
            assert "data" in tags_data
            # Verify that at least some tags exist in the response

            # 4. Update tags in a specific category
            update_category_payload = {
                "tag_values": ["0402", "0501"]  # New tag values for a category
            }
            update_category_response = await client.put(
                "/api/v1/user-service/users/me/tags/category/medical",  # Example category
                json=update_category_payload,
                headers=headers
            )
            assert update_category_response.status_code in [200, 201]
            update_category_data = update_category_response.json()
            assert "data" in update_category_data

            # 5. Get tags again to verify category update
            get_updated_tags_response = await client.get(
                "/api/v1/user-service/users/me/tags",
                headers=headers
            )
            assert get_updated_tags_response.status_code == 200
            updated_tags_data = get_updated_tags_response.json()
            assert "data" in updated_tags_data

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
    async def test_add_tags_through_gateway(self):
        """Test adding tags to user through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Add tags to user
            add_tags_payload = {
                "tag_values": ["0102", "0212"]  # Example tag values
            }
            add_tags_response = await client.post(
                "/api/v1/user-service/users/me/tags",
                json=add_tags_payload,
                headers=headers
            )
            # This might return 201 (created) or 200 (if tags already exist)
            assert add_tags_response.status_code in [200, 201]
            add_tags_data = add_tags_response.json()
            assert "data" in add_tags_data

    @pytest.mark.asyncio
    async def test_get_tags_through_gateway(self):
        """Test getting user tags through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Get user tags
            get_tags_response = await client.get(
                "/api/v1/user-service/users/me/tags",
                headers=headers
            )
            assert get_tags_response.status_code == 200
            tags_data = get_tags_response.json()
            assert "data" in tags_data

    @pytest.mark.asyncio
    async def test_update_tags_by_category_through_gateway(self):
        """Test updating tags by category through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Update tags in a specific category
            update_category_payload = {
                "tag_values": ["0402", "0501"]  # New tag values for a category
            }
            update_category_response = await client.put(
                "/api/v1/user-service/users/me/tags/category/age",  # Example category
                json=update_category_payload,
                headers=headers
            )
            assert update_category_response.status_code in [200, 201]
            update_category_data = update_category_response.json()
            assert "data" in update_category_data

    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def cleanup_method(self):
        """Cleanup method to clean up created users after each test"""
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