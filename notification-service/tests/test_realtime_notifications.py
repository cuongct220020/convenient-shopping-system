import asyncio
import websockets
import json
import urllib.request
import urllib.error
import time
import sys

# --- CONFIG ---
BASE_URL = "http://localhost:8000/api/v1/user-service"
WS_URL = "ws://localhost:8000/ws/v2/notification-service/notifications"

class Colors:
    OK = '\033[92m'
    FAIL = '\033[91m'
    WARN = '\033[93m'
    INFO = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

# --- API HELPERS ---

def api_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    body = None
    if data:
        body = json.dumps(data).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode('utf-8')
            return json.loads(resp_body) if resp_body else None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        print(f"{Colors.FAIL}API Error {e.code}: {err_body}{Colors.END}")
        return {"error": e.code, "body": err_body}
    except Exception as e:
        print(f"{Colors.FAIL}Request Failed: {e}{Colors.END}")
        raise

def register_and_login(username, email, password):
    print(f"{Colors.INFO}Setting up user: {username}...{Colors.END}")
    reg_data = {
        "username": username, "email": email, "password": password,
        "first_name": "Test", "last_name": username
    }
    
    # 1. Register
    resp = api_request("POST", "/auth/register", reg_data)
    
    # Check if registration was successful or user already exists
    if "error" in resp and resp["error"] == 409:
        print(f"  -> User already exists. Proceeding to login.")
    elif "error" in resp:
        print(f"{Colors.FAIL}  -> Registration failed: {resp['body']}{Colors.END}")
        # Proceed to login anyway in case it's a different issue, or fail later
    else:
        # Registration successful, account is inactive.
        # 2. Get OTP
        print(f"  -> Registration successful. Requesting OTP for activation...")
        otp_req = {"email": email, "action": "register"}
        otp_resp = api_request("POST", "/auth/otp/send", otp_req)
        
        if otp_resp and 'data' in otp_resp and otp_resp['data'] and 'otp_code' in otp_resp['data']:
            otp_code = otp_resp['data']['otp_code']
            print(f"  -> Got OTP: {otp_code}")
            
            # 3. Verify OTP
            verify_req = {"email": email, "otp_code": otp_code}
            verify_resp = api_request("POST", "/auth/otp/verify", verify_req)
            if "error" not in verify_resp:
                print(f"  -> {Colors.OK}Activation successful!{Colors.END}")
            else:
                print(f"{Colors.FAIL}  -> Activation failed: {verify_resp['body']}{Colors.END}")
        else:
            print(f"{Colors.WARN}  -> OTP code not returned (Check DEBUG mode). Activation might be manual.{Colors.END}")

    # 4. Login
    login_data = {"identifier": username, "password": password}
    resp = api_request("POST", "/auth/login", login_data)
    
    if "error" in resp:
        print(f"{Colors.FAIL}Login failed: {resp['body']}{Colors.END}")
        sys.exit(1)

    token = resp['data']['access_token']
    user_id = api_request("GET", "/users/me", token=token)['data']['user_id']
    return {"token": token, "user_id": user_id, "username": username}

# --- WS LISTENER ---

class NotificationReceiver:
    def __init__(self, user_info):
        self.user = user_info
        self.queue = asyncio.Queue()
        self.tasks = []
        self.websockets = []

    async def start(self):
        # Start user channel listener
        task = asyncio.create_task(self._run_user_channel())
        self.tasks.append(task)
        await asyncio.sleep(1) 

    async def _run_user_channel(self):
        url = f"{WS_URL}/users/{self.user['user_id']}"
        await self._connect_and_listen(url, "User Channel")

    async def _connect_and_listen(self, url, channel_name):
        headers = {"Authorization": f"Bearer {self.user['token']}"}
        try:
            # ping_interval=None to avoid interference
            async with websockets.connect(url, extra_headers=headers, ping_interval=None) as ws:
                self.websockets.append(ws)
                print(f"{Colors.OK}[{self.user['username']}] Connected to {channel_name}{Colors.END}")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    await self.queue.put(data)
                    print(f"\n{Colors.BOLD}🔔 [{self.user['username']}] ({channel_name}) Received: {data['event_type']}{Colors.END}")
        except Exception as e:
            # Ignore cancellation errors during cleanup
            if not isinstance(e, asyncio.CancelledError):
                print(f"{Colors.WARN}[{self.user['username']}] {channel_name} Closed: {e}{Colors.END}")

    async def wait_for_event(self, event_type, timeout=15):
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    msg = await asyncio.wait_for(self.queue.get(), timeout=1)
                    if msg['event_type'] == event_type:
                        return msg
                except asyncio.TimeoutError:
                    continue
            return None
        except Exception:
            return None

    def stop(self):
        for task in self.tasks: task.cancel()

# --- TEST SUITE ---

async def run_comprehensive_test():
    print(f"\n{Colors.BOLD}=== REALTIME NOTIFICATION TEST SUITE (FAMILY GROUP) ==={Colors.END}\n")
    
    # Generate random suffix for unique users
    import random
    suffix = f"{int(time.time())}_{random.randint(1000, 9999)}"

    # 1. Setup 3 Regular Users
    user_a = register_and_login(f"user_a_{suffix}", f"user_a_{suffix}@test.com", "Pass123!")
    user_b = register_and_login(f"user_b_{suffix}", f"user_b_{suffix}@test.com", "Pass123!")
    user_c = register_and_login(f"user_c_{suffix}", f"user_c_{suffix}@test.com", "Pass123!")

    # 2. Start Listeners (User Channel)
    receivers = {
        "user_a": NotificationReceiver(user_a),
        "user_b": NotificationReceiver(user_b),
        "user_c": NotificationReceiver(user_c)
    }
    for r in receivers.values(): await r.start()

    try:
        # SCENARIO 1: Create Group & Add Member
        print(f"\n{Colors.INFO}--- Scenario 1: Add User to Group ---{Colors.END}")
        print(f"[User A] Creating group...")
        group_resp = api_request("POST", "/groups", {"group_name": "Family Team"}, user_a['token'])
        group_id = group_resp['data']['id']
        
        print(f"[User A] Adding {user_b['username']} to group...")
        api_request("POST", f"/groups/{group_id}/members", {"identifier": user_b['username']}, user_a['token'])

        # Verify User B received notification
        notif = await receivers["user_b"].wait_for_event("group_user_added")
        if notif:
            print(f"{Colors.OK}✅ User B received notification successfully!{Colors.END}")
        else:
            print(f"{Colors.FAIL}❌ User B did not receive notification.{Colors.END}")

        # SCENARIO 2: Update Head Chef Role
        print(f"\n{Colors.INFO}--- Scenario 2: Update Head Chef Role ---{Colors.END}")
        print(f"[User A] Transferring Head Chef to {user_b['username']}...")
        api_request("PATCH", f"/groups/{group_id}/members/{user_b['user_id']}", {"role": "head_chef"}, user_a['token'])
        
        # Verify User B (new chef) receives it
        notif = await receivers["user_b"].wait_for_event("group_head_chef_updated")
        if notif:
            print(f"{Colors.OK}✅ New Head Chef (User B) notified!{Colors.END}")
        else:
            print(f"{Colors.FAIL}❌ New Head Chef not notified.{Colors.END}")
            
        # Verify User A also receives update (via Group Channel)
        notif_a = await receivers["user_a"].wait_for_event("group_head_chef_updated")
        if notif_a:
             print(f"{Colors.OK}✅ User A notified of role change!{Colors.END}")

        # SCENARIO 3: Remove Member
        print(f"\n{Colors.INFO}--- Scenario 3: Remove Member ---{Colors.END}")
        print(f"[User B] Adding {user_c['username']} to group...")
        api_request("POST", f"/groups/{group_id}/members", {"identifier": user_c['username']}, user_b['token'])
        await receivers["user_c"].wait_for_event("group_user_added") # Clear queue
        
        print(f"[User B] Removing {user_c['username']} from group...")
        api_request("DELETE", f"/groups/{group_id}/members/{user_c['user_id']}", None, user_b['token'])
        
        # Verify notifications
        notif = await receivers["user_c"].wait_for_event("group_user_removed")
        if notif:
            print(f"{Colors.OK}✅ User C received removal notification!{Colors.END}")
        else:
            print(f"{Colors.FAIL}❌ User C not notified of removal.{Colors.END}")

        # SCENARIO 4: User Leave Group (Head Chef Leaves -> Auto Promote)
        print(f"\n{Colors.INFO}--- Scenario 4: Head Chef Leaves (Auto-Promote) ---{Colors.END}")
        
        print(f"[User B] Leaving group (as Head Chef)...")
        api_request("DELETE", f"/groups/{group_id}/members/me", None, user_b['token'])
        
        print(f"Waiting for auto-promotion and leave notifications...")
        
        # Verify User A (remaining member) gets notified
        promote_notif = await receivers["user_a"].wait_for_event("group_head_chef_updated")
        if promote_notif and promote_notif['data']['new_head_chef_id'] == user_a['user_id']:
            print(f"{Colors.OK}✅ User A correctly auto-promoted to Head Chef!{Colors.END}")
        else:
            print(f"{Colors.FAIL}❌ User A not notified of Head Chef update.{Colors.END}")

        leave_notif = await receivers["user_a"].wait_for_event("group_user_left")
        if leave_notif:
            print(f"{Colors.OK}✅ User A notified that User B left.{Colors.END}")
        else:
            print(f"{Colors.FAIL}❌ User A not notified of user leaving.{Colors.END}")

    finally:
        print(f"\n{Colors.INFO}Cleaning up...{Colors.END}")
        for r in receivers.values(): r.stop()
        print(f"{Colors.BOLD}Test Suite Finished.{Colors.END}")

if __name__ == "__main__":
    try:
        asyncio.run(run_comprehensive_test())
    except KeyboardInterrupt:
        pass
