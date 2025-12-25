import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy import select
from app.models.user import User

# --- Mock Redis Helper ---
class AsyncMockRedis:
    def __init__(self):
        self.store = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ex=None, nx=False):
        if nx and key in self.store:
            return None
        self.store[key] = value
        return True

    async def delete(self, key):
        if key in self.store:
            del self.store[key]
            return 1
        return 0

@pytest.mark.asyncio
async def test_register_verify_login_integration(test_client, db_session):
    """
    Integration Test: Full Authentication Flow
    Scenario:
      1. Register a new user (Happy Path)
      2. Verify OTP (using mocked Redis but real Service logic)
      3. Login (verify DB state and Token generation)
    """

    # === Setup Mocks ===
    mock_redis = AsyncMockRedis()
    
    # We mock:
    # 1. Kafka: To avoid connection errors.
    # 2. Redis: To store OTPs in memory (mock_redis).
    # 3. Random: To predict the OTP code.
    
    with patch("app.services.kafka_service.KafkaService.publish_user_registration_otp", new_callable=AsyncMock) as mock_kafka, \
         patch("shopping_shared.caching.redis_manager.redis_manager.client", mock_redis), \
         patch("random.randint", return_value=123456):

        # === Step 1: Register User ===
        email_test = "integration@example.com"
        reg_payload = {
            "username": "integration_user",
            "email": email_test,
            "password": "StrongPassword123!",
            "first_name": "Integration",
            "last_name": "Test"
        }

        request, response = await test_client.post("/api/v1/user-service/auth/register", json=reg_payload)

        # Assertions for Step 1
        assert response.status == 201, f"Register failed: {response.text}"
        assert response.json["status"] == "success"
        assert response.json["data"]["email"] == email_test
        
        # Verify Kafka was called (simulating email sending trigger)
        mock_kafka.assert_called_once()
        
        # Verify User is created in DB but NOT active yet
        # Need to query DB. db_session fixture provided by conftest.
        result = await db_session.execute(select(User).where(User.email == email_test))
        user_in_db = result.scalar_one_or_none()
        assert user_in_db is not None
        assert user_in_db.is_active is False

        # === Step 2: Verify OTP ===
        # Since we mocked random.randint to return 123456, we know the code.
        # And we used MockRedis, so OTPService should have stored the hash in our mock_redis.
        
        verify_payload = {
            "email": email_test,
            "otp_code": "123456",
            "action": "register"
        }

        request, response = await test_client.post("/api/v1/user-service/auth/otp/verify", json=verify_payload)

        # Assertions for Step 2
        assert response.status == 200, f"OTP Verify failed: {response.text}"
        assert response.json["status"] == "success"

        # Verify User is now ACTIVE
        # We need to expire/refresh the session or query again
        db_session.expire_all()
        result = await db_session.execute(select(User).where(User.email == email_test))
        user_in_db = result.scalar_one()
        assert user_in_db.is_active is True

        # === Step 3: Login ===
        login_payload = {
            "identifier": "integration_user",
            "password": "StrongPassword123!"
        }

        request, response = await test_client.post("/api/v1/user-service/auth/login", json=login_payload)

        # Assertions for Step 3
        assert response.status == 200, f"Login failed: {response.text}"
        data = response.json["data"]
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"

        # Verify Refresh Token is stored in Redis (Allowlist)
        # The key format is "user-service:session:<user_id>"
        # We can check if *some* key exists in our mock_redis that looks like a session
        user_id_str = str(user_in_db.id)
        session_key = f"user-service:session:{user_id_str}"
        stored_jti = await mock_redis.get(session_key)
        assert stored_jti is not None
