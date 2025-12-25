## Testing Auth Endpoints

### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "cuongct090204",
    "email": "cuongct.ittnk67@gmail.com",
    "password": "cuongdeptrai1",
    "first_name": "Cuong",
    "last_name": "CT"
  }'
```

**Note:**
- The `X-Idempotency-Key` header is required due to the idempotency decorator in the view
- You can generate an idempotency key using the `uuidgen` command or use any unique string
- The fields in the payload must match the `RegisterRequestSchema`

### Verify OTP
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cuongct.ittnk67@gmail.com",
    "otp_code": "412642",
    "action": "register"
  }'
```

### Login with existing user
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "cuongct090204",
    "password": "cuongdeptrai1"
  }'
```

**Note:**
- The `identifier` field can be either username or email
- The response will include access token and set refresh token as an HttpOnly cookie

### Logout (requires access token)33
```bash
curl -X POST http://localhost:8000/api/v1/user-service/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzaG9wcGluZy11c2VyLXNlcnZpY2UiLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY2NjUzNTg1LCJpYXQiOjE3NjY2NTI2ODUsInN1YiI6ImU5YzdlZDQ1LTRiMzUtNGY2MC05ZDNiLTM5MTc1Nzk5OGQ3ZCIsImp0aSI6Ijc1ODQ5OGY1LTFhZGEtNDdjZS1hYzczLTBiZGZkMzBhZDE3MiIsImF1ZCI6InNob3BwaW5nLXN5c3RlbS11c2VycyIsInN5c3RlbV9yb2xlIjoidXNlciIsImVtYWlsIjoiY3VvbmdjdC5pdHRuazY3QGdtYWlsLmNvbSJ9.l8xOBGmu12K4u275SqLtpA3rTQNq4v9ufkj3K_BXukCE0xaem_Pj3gTxKitlccmXYpXCAvXWVFXqcfEyVAjQggzkKWKrkch_s4BDh0BfbHT799vKWMP3gME8ljc9h2hL7q-5cZ_itviVulaEeTSZ_tojwgKtsb_eIBLjLqw-8w_vW-z8B-thSozKRaU68-VgAFsSeXreUyAtaZdzQtyg5y84NdaFSwP-f9Ux5G5tWUe8lUPoLgzWAcyqsje0-sgTBmCKiLVB3sLn6JtYMsqycQwt1bBzt8U3QJXgwDbt-wZ_yCj_IQ8Q_YMQe1p2l73H0hBKz1zLnql-MpEoRVW_-g" \
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
[README.md](README.md)
### Send OTP for various actions
```bash
# For password reset
curl -X POST http://localhost:8000/api/v1/user-service/auth/otp/send \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cuongct.ittnk67@gmail.com", 
    "action": "reset_password"
  }'
```

**Note:**
- The `action` field must be one of: "register", "reset_password", or "change_email"
- For security, the response will always be generic regardless of whether the email exists



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