### API Testing

#### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser123",
    "email": "testuser@example.com",
    "password": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

If you're running the service on a different port (e.g., 9001 as specified in docker-compose), update the URL accordingly:

```bash
curl -X POST http://localhost:9001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: $(uuidgen)" \
  -d '{
    "username": "testuser123",
    "email": "testuser@example.com",
    "password": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User",
    "phone_num": "+1234567890"
  }'
```

**Note:**
- The `X-Idempotency-Key` header is required due to the idempotency decorator in the view
- You can generate an idempotency key using the `uuidgen` command or use any unique string
- The fields in the payload must match the `RegisterRequestSchema`