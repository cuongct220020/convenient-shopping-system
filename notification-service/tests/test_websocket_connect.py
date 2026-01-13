import asyncio
import websockets
import sys
import json
import urllib.request
import urllib.error
import base64

# --- CẤU HÌNH TỰ ĐỘNG ---
AUTH_GATEWAY_URL = "http://localhost:8000/api/v1/user-service/auth/login"
USERNAME = "userB"
PASSWORD = "userABCDEF"

class Colors:
    OK = '\033[92m'
    FAIL = '\033[91m'
    WARN = '\033[93m'
    INFO = '\033[94m'
    END = '\033[0m'

def get_auth_data():
    """Đăng nhập để lấy Token mới"""
    print(f"{Colors.INFO}🔄 Đang đăng nhập tài khoản: {USERNAME}...{Colors.END}")
    payload = json.dumps({"identifier": USERNAME, "password": PASSWORD}).encode('utf-8')
    req = urllib.request.Request(
        AUTH_GATEWAY_URL, 
        data=payload, 
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            body = json.loads(response.read().decode('utf-8'))
            token = body['data']['access_token']
            print(f"{Colors.OK}✅ Đăng nhập thành công!{Colors.END}")
            return token
    except Exception as e:
        print(f"{Colors.FAIL}❌ Lỗi đăng nhập: {e}{Colors.END}")
        sys.exit(1)

def decode_token(token):
    """Giải mã Token để lấy thông tin User"""
    try:
        payload_part = token.split('.')[1]
        payload_part += '=' * (-len(payload_part) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_part).decode('utf-8'))
        return payload.get('sub'), payload.get('email'), payload.get('system_role', 'user')
    except Exception as e:
        print(f"{Colors.FAIL}❌ Lỗi giải mã token: {e}{Colors.END}")
        sys.exit(1)

async def test_connection(name, uri, headers=None):
    print(f"\n--- TEST: {name} ---")
    print(f"Target: {uri}")
    
    try:
        # Thử kết nối dùng additional_headers (Websockets 14+) hoặc extra_headers (cũ)
        try:
            async with websockets.connect(uri, additional_headers=headers, open_timeout=5) as ws:
                print(f"{Colors.OK}✅ KẾT NỐI THÀNH CÔNG!{Colors.END}")
                await ws.close()
                return True
        except TypeError:
            async with websockets.connect(uri, extra_headers=headers, open_timeout=5) as ws:
                print(f"{Colors.OK}✅ KẾT NỐI THÀNH CÔNG!{Colors.END}")
                await ws.close()
                return True

    except Exception as e:
        error_msg = str(e)
        status_code = getattr(e, 'status_code', None)
        if not status_code and "Status code" in error_msg:
            try: status_code = int(error_msg.split("Status code")[1].split(" ")[1].strip())
            except: pass

        if status_code:
            print(f"{Colors.FAIL}❌ LỖI HTTP STATUS: {status_code}{Colors.END}")
            if status_code == 404:
                print("  -> 404 Not Found: Đường dẫn URL sai. Kiểm tra lại Blueprint prefix.")
            elif status_code == 403:
                print("  -> 403 Forbidden: User ID trong URL không khớp với Token.")
            elif status_code == 502:
                print("  -> 502 Bad Gateway: Notification Service (9005) chưa chạy.")
        else:
            print(f"{Colors.FAIL}❌ LỖI: {error_msg}{Colors.END}")
        return False

async def main():
    # 1. Khởi tạo dữ liệu
    token = get_auth_data()
    user_id, email, role = decode_token(token)
    
    print(f"{Colors.INFO}ℹ️  User ID: {user_id}{Colors.END}")
    print(f"{Colors.INFO}ℹ️  Path: /ws/v1/notifications/users/{user_id}{Colors.END}")

    # 2. TEST TRỰC TIẾP SERVICE (9005)
    # Đường dẫn trong Sanic sau khi bỏ prefix dư thừa là /ws/v1/notifications/...
    direct_url = f"ws://localhost:9005/ws/v2/notification-service/notifications/users/{user_id}"
    direct_headers = {
        "Authorization": f"Bearer {token}",
        "X-User-ID": user_id,
        "X-JTI": "debug-jti",
        "X-User-Role": role,
        "X-User-Email": email
    }
    
    print("\n[BƯỚC 1] Kiểm tra kết nối trực tiếp đến Service (Port 9005)")
    service_ok = await test_connection("Direct Service", direct_url, direct_headers)
    
    if not service_ok:
        print(f"\n{Colors.WARN}⚠️ Vui lòng đảm bảo đã chạy: python notification-service/run.py{Colors.END}")
        return

    # 3. TEST QUA KONG (8000)
    kong_url = f"ws://localhost:8000/ws/v2/notification-service/notifications/users/{user_id}"
    kong_headers = {"Authorization": f"Bearer {token}"}
    
    print("\n[BƯỚC 2] Kiểm tra qua Kong Gateway (Port 8000)")
    await test_connection("Kong Gateway", kong_url, kong_headers)

    # 4. TEST QUA KONG (Query Param)
    kong_query_url = f"{kong_url}?jwt={token}"
    print("\n[BƯỚC 3] Kiểm tra qua Kong dùng Query Parameter (?jwt=...)")
    await test_connection("Kong Query Param", kong_query_url)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
