#!/usr/bin/env python3
"""
Comprehensive Test Script for User Profile APIs using pytest.
Tests the complete user journey: register, login, view core info, identity profile, health profile, change password, change email.
"""
import pytest
import pytest_asyncio
import time
import uuid


class TestUserProfileManagementThroughGateway:
    """Test class for user profile management workflows through Kong Gateway"""

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
        self.username = f"profile_user_{ts}_{random_suffix}"
        self.email = f"profile_user_{ts}_{random_suffix}@example.com"
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
                    "first_name": "Profile",
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
    async def test_complete_user_profile_workflow(self):
        """Test the complete user profile workflow: register -> login -> view core info -> identity profile -> health profile -> change password -> change email"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # 1. View core info
            get_core_response = await client.get(
                "/api/v1/user-service/users/me",
                headers=headers
            )
            assert get_core_response.status_code == 200
            core_data = get_core_response.json()
            assert "data" in core_data
            assert core_data["data"]["username"] == self.username
            assert core_data["data"]["email"] == self.email

            # 2. View identity profile
            get_identity_response = await client.get(
                "/api/v1/user-service/users/me/profile/identity",
                headers=headers
            )
            # Identity profile might not exist yet, so it could be 200 or 404
            assert get_identity_response.status_code in [200, 404]

            # 3. Update identity profile
            identity_payload = {
                "identity_number": "ID123456789",
                "identity_issued_date": "2023-01-01",
                "identity_issued_place": "Hanoi",
                "date_of_birth": "1990-01-01",
                "gender": "male"
            }
            update_identity_response = await client.patch(
                "/api/v1/user-service/users/me/profile/identity",
                json=identity_payload,
                headers=headers
            )
            assert update_identity_response.status_code == 200
            identity_data = update_identity_response.json()
            assert "data" in identity_data

            # 4. View health profile
            get_health_response = await client.get(
                "/api/v1/user-service/users/me/profile/health",
                headers=headers
            )
            # Health profile might not exist yet, so it could be 200 or 404
            assert get_health_response.status_code in [200, 404]

            # 5. Update health profile
            health_payload = {
                "height": 175,
                "weight": 70,
                "blood_type": "O+",
                "allergies": "Peanuts",
                "chronic_diseases": "Diabetes",
                "current_medications": "Insulin"
            }
            update_health_response = await client.patch(
                "/api/v1/user-service/users/me/profile/health",
                json=health_payload,
                headers=headers
            )
            assert update_health_response.status_code == 200
            health_data = update_health_response.json()
            assert "data" in health_data

            # 6. Change password
            change_password_payload = {
                "current_password": self.password,
                "new_password": "NewSecurePassword123!"
            }
            change_password_response = await client.post(
                "/api/v1/user-service/users/me/change-password",
                json=change_password_payload,
                headers=headers
            )
            assert change_password_response.status_code == 200

            # 7. Verify login with new password
            new_password = "NewSecurePassword123!"
            login_new_response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": self.username,
                    "password": new_password
                },
                headers={"Content-Type": "application/json"}
            )
            assert login_new_response.status_code == 200
            self.password = new_password  # Update for potential future use

            # 8. Change email
            new_email = f"updated_{self.email}"
            change_email_payload = {
                "email": new_email
            }
            change_email_response = await client.patch(
                "/api/v1/user-service/users/me",
                json=change_email_payload,
                headers=headers
            )
            assert change_email_response.status_code == 200
            updated_user_data = change_email_response.json()
            assert updated_user_data["data"]["email"] == new_email

            # 9. Verify email was updated by getting user info again
            get_updated_response = await client.get(
                "/api/v1/user-service/users/me",
                headers=headers
            )
            assert get_updated_response.status_code == 200
            updated_data = get_updated_response.json()
            assert updated_data["data"]["email"] == new_email

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
    async def test_view_core_info_through_gateway(self):
        """Test viewing core user information through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Get core info
            get_core_response = await client.get(
                "/api/v1/user-service/users/me",
                headers=headers
            )
            assert get_core_response.status_code == 200
            core_data = get_core_response.json()
            assert "data" in core_data
            assert core_data["data"]["username"] == self.username
            assert core_data["data"]["email"] == self.email
            assert core_data["data"]["id"] == self.user_id

    @pytest.mark.asyncio
    async def test_view_identity_profile_through_gateway(self):
        """Test viewing identity profile through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Get identity profile (might not exist yet)
            get_identity_response = await client.get(
                "/api/v1/user-service/users/me/profile/identity",
                headers=headers
            )
            # Should return 200 or 404 (not found if not created yet)
            assert get_identity_response.status_code in [200, 404]

            # Create identity profile first
            identity_payload = {
                "identity_number": "ID987654321",
                "identity_issued_date": "2022-05-15",
                "identity_issued_place": "Ho Chi Minh City",
                "date_of_birth": "1985-03-20",
                "gender": "female"
            }
            update_identity_response = await client.patch(
                "/api/v1/user-service/users/me/profile/identity",
                json=identity_payload,
                headers=headers
            )
            assert update_identity_response.status_code == 200

            # Now get the identity profile
            get_identity_response = await client.get(
                "/api/v1/user-service/users/me/profile/identity",
                headers=headers
            )
            assert get_identity_response.status_code == 200
            identity_data = get_identity_response.json()
            assert "data" in identity_data
            assert identity_data["data"]["identity_number"] == "ID987654321"

    @pytest.mark.asyncio
    async def test_view_health_profile_through_gateway(self):
        """Test viewing health profile through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Get health profile (might not exist yet)
            get_health_response = await client.get(
                "/api/v1/user-service/users/me/profile/health",
                headers=headers
            )
            # Should return 200 or 404 (not found if not created yet)
            assert get_health_response.status_code in [200, 404]

            # Create health profile first
            health_payload = {
                "height": 165,
                "weight": 60,
                "blood_type": "A+",
                "allergies": "Dust",
                "chronic_diseases": "Asthma",
                "current_medications": "Inhaler"
            }
            update_health_response = await client.patch(
                "/api/v1/user-service/users/me/profile/health",
                json=health_payload,
                headers=headers
            )
            assert update_health_response.status_code == 200

            # Now get the health profile
            get_health_response = await client.get(
                "/api/v1/user-service/users/me/profile/health",
                headers=headers
            )
            assert get_health_response.status_code == 200
            health_data = get_health_response.json()
            assert "data" in health_data
            assert health_data["data"]["blood_type"] == "A+"

    @pytest.mark.asyncio
    async def test_change_password_through_gateway(self):
        """Test changing password through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Change password
            change_password_payload = {
                "current_password": self.password,
                "new_password": "AnotherSecurePassword123!"
            }
            change_password_response = await client.post(
                "/api/v1/user-service/users/me/change-password",
                json=change_password_payload,
                headers=headers
            )
            assert change_password_response.status_code == 200

            # Verify login with new password
            new_password = "AnotherSecurePassword123!"
            login_new_response = await client.post(
                "/api/v1/user-service/auth/login",
                json={
                    "identifier": self.username,
                    "password": new_password
                },
                headers={"Content-Type": "application/json"}
            )
            assert login_new_response.status_code == 200
            self.password = new_password  # Update for potential future use

    @pytest.mark.asyncio
    async def test_change_email_through_gateway(self):
        """Test changing email through Kong gateway"""
        import httpx
        headers = {"Authorization": f"Bearer {self.user_token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Change email
            new_email = f"changed_{int(time.time())}@example.com"
            change_email_payload = {
                "email": new_email
            }
            change_email_response = await client.patch(
                "/api/v1/user-service/users/me",
                json=change_email_payload,
                headers=headers
            )
            assert change_email_response.status_code == 200
            updated_user_data = change_email_response.json()
            assert updated_user_data["data"]["email"] == new_email

            # Verify email was updated by getting user info again
            get_updated_response = await client.get(
                "/api/v1/user-service/users/me",
                headers=headers
            )
            assert get_updated_response.status_code == 200
            updated_data = get_updated_response.json()
            assert updated_data["data"]["email"] == new_email

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