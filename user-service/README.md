## Testing Auth Endpoints

### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/register \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: $(uuidgen)" \
  -d '{
    "username": "testuser123",
    "email": "testuser@example.com",
    "password": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Note:**
- The `X-Idempotency-Key` header is required due to the idempotency decorator in the view
- You can generate an idempotency key using the `uuidgen` command or use any unique string
- The fields in the payload must match the `RegisterRequestSchema`

### Login with existing user
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "testuser123",
    "password": "SecurePassword123!"
  }'
```

**Note:**
- The `identifier` field can be either username or email
- The response will include access token and set refresh token as an HttpOnly cookie

### Logout (requires access token)
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/logout \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json"
```

**Note:**
- Requires a valid access token in the Authorization header
- The refresh token cookie will be cleared upon successful logout

### Refresh access token (requires refresh token cookie)
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/refresh-token \
  -H "Content-Type: application/json" \
  --cookie "refresh_token=<REFRESH_TOKEN>"
```

**Note:**
- Requires the refresh token to be sent as an HttpOnly cookie
- Returns a new access token and may rotate the refresh token

### Send OTP for various actions
```bash
# For registration verification
curl -X POST http://localhost:8000/api/v1/user-service/auth/otp/send \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "action": "register"
  }'

# For password reset
curl -X POST http://localhost:8000/api/v1/user-service/auth/otp/send \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "action": "reset_password"
  }'

# For email change
curl -X POST http://localhost:8000/api/v1/user-service/auth/otp/send \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "action": "change_email"
  }'
```

**Note:**
- The `action` field must be one of: "register", "reset_password", or "change_email"
- For security, the response will always be generic regardless of whether the email exists

### Verify OTP
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "otp_code": "123456",
    "action": "register"
  }'
```

**Note:**
- The `action` field must match the one used when sending the OTP
- The `otp_code` is typically 6 digits
- For "register" action, successful verification will activate the user account

### Reset password (after OTP verification)
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "otp_code": "123456",
    "new_password": "NewSecurePassword123!"
  }'
```

**Note:**
- Requires a valid OTP that was sent for "reset_password" action
- The new password must meet the same requirements as during registration