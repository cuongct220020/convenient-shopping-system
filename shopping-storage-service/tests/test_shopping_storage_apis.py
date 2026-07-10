import requests
import json
import random
import string
import time
import uuid
from datetime import datetime, timedelta

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://dichotienloi.com"
VERIFY_SSL = False

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BLUE = '\033[94m'

def print_success(msg):
    print(f"{GREEN}[PASS] {msg}{RESET}")

def print_error(msg):
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}[INFO] {msg}{RESET}")

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

context = {
    "headers": {},
    "group_id": None,
    "storage_id": None,
    "unit_id": None,
    "plan_id": None,
    "user_id": None,
    "user_email": None
}

def setup_auth_and_group():
    print_info("--- 1. SETUP - User & Group ---")
    
    # 1. Register a fresh user
    email = f"user_{random_string()}@example.com".lower()
    password = "Password123!"
    username = f"user_{random_string()}"
    context["user_email"] = email

    print_info(f"Registering {email}...")
    resp = requests.post(
        f"{BASE_URL}/api/v1/user-service/auth/register",
        json={"username": username, "email": email, "password": password},
        verify=VERIFY_SSL
    )
    if resp.status_code not in [200, 201]:
        print_error(f"Register failed: {resp.text}")
        return False

    # 2. OTP Verification
    print_info("Requesting OTP...")
    resp = requests.post(
        f"{BASE_URL}/api/v1/user-service/auth/otp/send",
        json={"email": email, "action": "register"},
        verify=VERIFY_SSL
    )
    otp_code = resp.json().get("data", {}).get("otp_code")
    if not otp_code:
        print_error("Failed to get OTP (Make sure server is in DEBUG mode)")
        return False
    
    print_info(f"Verifying OTP: {otp_code}...")
    resp = requests.post(
        f"{BASE_URL}/api/v1/user-service/auth/otp/verify",
        json={"email": email, "otp_code": otp_code},
        verify=VERIFY_SSL
    )
    if resp.status_code != 200:
        print_error("OTP Verification failed")
        return False

    # 3. Login
    print_info("Logging in...")
    resp = requests.post(
        f"{BASE_URL}/api/v1/user-service/auth/login",
        json={"identifier": email, "password": password},
        verify=VERIFY_SSL
    )
    
    if resp.status_code == 200:
        response_json = resp.json()
        token = response_json.get("data", {}).get("access_token")
        user_info = response_json.get("data", {}).get("user", {})
        context["headers"] = {"Authorization": f"Bearer {token}"}
        
        # Get User ID UUID
        print_info("Fetching User Profile...")
        me_resp = requests.get(f"{BASE_URL}/api/v1/user-service/users/me", headers=context["headers"], verify=VERIFY_SSL)
        if me_resp.status_code == 200:
            context["user_id"] = me_resp.json()["data"]["user_id"]
            print_success(f"Logged in successfully. User ID: {context['user_id']}")
        else:
            print_error(f"Failed to get user profile: {me_resp.text}")
            return False
    else:
        print_error(f"Login failed: {resp.text}")
        return False

    # 4. Create Group
    print_info("Creating Group...")
    resp = requests.post(
        f"{BASE_URL}/api/v1/user-service/groups",
        json={"group_name": f"Test Group {random_string()}"},
        headers=context["headers"],
        verify=VERIFY_SSL
    )
    if resp.status_code == 201:
        context["group_id"] = resp.json()["data"]["id"]
        print_success(f"Created Group ID: {context['group_id']}")
        return True
    else:
        print_error(f"Group creation failed: {resp.text}")
        return False

def test_storage_apis():
    print_info("\n--- 2. STORAGES API ---")
    
    if not context["group_id"]:
        print_error("Skipping Storages API tests: No Group ID")
        return False

    # Create Storage
    payload = {
        "storage_name": "My Smart Fridge",
        "storage_type": "fridge",
        "group_id": context["group_id"]
    }
    resp = requests.post(f"{BASE_URL}/v1/storages/", json=payload, headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 201:
        data = resp.json()
        context["storage_id"] = data["storage_id"]
        print_success(f"Created Storage: {data['storage_name']} (ID: {context['storage_id']})")
    else:
        print_error(f"Failed to create storage: {resp.text}")
        return False

    # Get Storage By ID
    resp = requests.get(f"{BASE_URL}/v1/storages/{context['storage_id']}", headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 200:
        print_success(f"Get Storage By ID: OK - {resp.json()['storage_name']}")
    else:
        print_error(f"Get Storage By ID failed: {resp.text}")

    # Update Storage
    resp = requests.put(
        f"{BASE_URL}/v1/storages/{context['storage_id']}", 
        json={"storage_name": "Main Kitchen Fridge"}, 
        headers=context["headers"], 
        verify=VERIFY_SSL
    )
    if resp.status_code == 200:
        print_success(f"Updated Storage: {resp.json()['storage_name']}")

    # List Storages
    resp = requests.get(f"{BASE_URL}/v1/storages/", headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 200:
        print_success(f"List Storages: OK (Found {len(resp.json()['data'])} items)")

    # Delete Storage (Create a temporary one to delete)
    print_info("Testing Delete Storage...")
    temp_payload = {
        "storage_name": "Temp Fridge",
        "storage_type": "fridge",
        "group_id": context["group_id"]
    }
    temp_resp = requests.post(f"{BASE_URL}/v1/storages/", json=temp_payload, headers=context["headers"], verify=VERIFY_SSL)
    if temp_resp.status_code == 201:
        temp_id = temp_resp.json()["storage_id"]
        del_resp = requests.delete(f"{BASE_URL}/v1/storages/{temp_id}", headers=context["headers"], verify=VERIFY_SSL)
        if del_resp.status_code == 204:
            print_success(f"Deleted Storage ID: {temp_id}")
        else:
            print_error(f"Failed to delete storage: {del_resp.text}")
        
    return True

def test_storable_unit_apis():
    print_info("\n--- 3. STORABLE UNITS API ---")
    
    if not context["storage_id"]:
        print_error("Skipping Storable Units tests: No Storage ID")
        return False
    
    # 1. Create Storable Unit (Countable)
    payload = {
        "unit_name": "Cà chua bi",
        "storage_id": context["storage_id"],
        "package_quantity": 10,
        "component_id": 298, # Giả định ID từ Recipe Service
        "content_type": "countable_ingredient"
    }
    resp = requests.post(f"{BASE_URL}/v1/storable_units/", json=payload, headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 201:
        context["unit_id"] = resp.json()["unit_id"]
        print_success(f"Created Storable Unit: {resp.json()['unit_name']} (ID: {context['unit_id']})")
    else:
        print_error(f"Failed to create unit: {resp.text}")
        return False

    # 2. Get Unit By ID
    resp = requests.get(f"{BASE_URL}/v1/storable_units/{context['unit_id']}", headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 200:
        print_success(f"Get Unit By ID: OK - {resp.json()['unit_name']}")
    else:
        print_error(f"Get Unit By ID failed: {resp.text}")

    # 3. Update Unit
    update_payload = {"unit_name": "Cà chua bi tươi"}
    resp = requests.put(f"{BASE_URL}/v1/storable_units/{context['unit_id']}", json=update_payload, headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 200:
        print_success(f"Updated Unit name: {resp.json()['unit_name']}")
    else:
        print_error(f"Update Unit failed: {resp.text}")

    # 4. Get Stacked Units
    resp = requests.get(
        f"{BASE_URL}/v1/storable_units/stacked", 
        params={"storage_id": context["storage_id"]},
        headers=context["headers"], 
        verify=VERIFY_SSL
    )
    if resp.status_code == 200:
        print_success(f"Get Stacked Units: Found {len(resp.json()['data'])} stacked groups")

    # 5. Filter Units
    resp = requests.get(
        f"{BASE_URL}/v1/storable_units/filter", 
        params={"group_id": context["group_id"]},
        headers=context["headers"], 
        verify=VERIFY_SSL
    )
    if resp.status_code == 200:
        print_success(f"Filter Units by Group: Found {len(resp.json()['data'])} items")

    # 6. Get Many Units (List)
    resp = requests.get(f"{BASE_URL}/v1/storable_units/", headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 200:
        print_success(f"List All Units: Found {len(resp.json()['data'])} items")

    # 7. Consume Unit
    resp = requests.post(
        f"{BASE_URL}/v1/storable_units/{context['unit_id']}/consume", 
        params={"consume_quantity": 3},
        headers=context["headers"], 
        verify=VERIFY_SSL
    )
    if resp.status_code == 200:
        print_success(f"Consumed 3 units: {resp.json()['message']}")
        
    return True

def test_shopping_plan_apis():
    print_info("\n--- 4. SHOPPING PLANS API ---")
    
    if not context["group_id"] or not context["user_id"]:
        print_error("Skipping Shopping Plans tests: Missing Group ID or User ID")
        return False
    
    # === Sub-flow 1: Completion Flow (Create -> Assign -> Update -> Report) ===
    print_info("--- Flow 1: Completion Flow ---")
    
    # 1. Create Plan
    deadline = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
    payload = {
        "group_id": context["group_id"],
        "deadline": deadline,
        "assigner_id": context["user_id"],
        "shopping_list": [
            {
                "type": "uncountable_ingredient",
                "unit": "ML",
                "quantity": 1000,
                "component_id": 424, # Sữa tươi
                "component_name": "Sữa tươi"
            }
        ],
        "others": {"note": "Mua loại không đường"}
    }
    resp = requests.post(f"{BASE_URL}/v1/shopping_plans/", json=payload, headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 201:
        context["plan_id"] = resp.json()["plan_id"]
        print_success(f"Created Shopping Plan (ID: {context['plan_id']})")
    else:
        print_error(f"Failed to create plan: {resp.text}")
        return False

    # 2. Get Plan By ID
    resp = requests.get(f"{BASE_URL}/v1/shopping_plans/{context['plan_id']}", headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 200:
        print_success("Get Plan By ID: OK")
    
    # 3. Update Plan
    update_payload = {"others": {"note": "Updated note: Mua loại TH True Milk"}}
    resp = requests.put(f"{BASE_URL}/v1/shopping_plans/{context['plan_id']}", json=update_payload, headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 200:
        print_success("Updated Plan: OK")

    # 4. Assign Plan
    resp = requests.post(
        f"{BASE_URL}/v1/shopping_plans/{context['plan_id']}/assign", 
        params={"assignee_id": context["user_id"]},
        headers=context["headers"], 
        verify=VERIFY_SSL
    )
    if resp.status_code == 200:
        print_success("Plan assigned to current user (IN_PROGRESS)")

    # 5. Report Completion (Finish Plan)
    if context["storage_id"]:
        report_payload = {
            "plan_id": context["plan_id"],
            "spent_amount": 30000,
            "report_content": [
                {
                    "storage_id": context["storage_id"],
                    "package_quantity": 2,
                    "unit_name": "Sữa tươi TH 500ml",
                    "component_id": 424,
                    "content_type": "uncountable_ingredient",
                    "content_quantity": 1000.0,
                    "content_unit": "ML"
                }
            ]
        }
        resp = requests.post(
            f"{BASE_URL}/v1/shopping_plans/{context['plan_id']}/report", 
            params={"assignee_id": context["user_id"], "confirm": "true"},
            json=report_payload, 
            headers=context["headers"], 
            verify=VERIFY_SSL
        )
        if resp.status_code == 200:
            print_success(f"Plan Reported & Completed: {resp.json()['message']}")
        else:
            print_error(f"Report failed: {resp.text}")

    # 6. Filter Plans
    resp = requests.get(
        f"{BASE_URL}/v1/shopping_plans/filter", 
        params={"group_id": context["group_id"], "plan_status": "completed"},
        headers=context["headers"], 
        verify=VERIFY_SSL
    )
    if resp.status_code == 200:
        print_success(f"Filter Completed Plans: Found {len(resp.json()['data'])} items")

    # === Sub-flow 2: Unassign Flow ===
    print_info("--- Flow 2: Unassign Flow ---")
    payload["shopping_list"][0]["component_name"] = "Bánh mì"
    resp = requests.post(f"{BASE_URL}/v1/shopping_plans/", json=payload, headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 201:
        temp_plan_id = resp.json()["plan_id"]
        # Assign
        requests.post(f"{BASE_URL}/v1/shopping_plans/{temp_plan_id}/assign", params={"assignee_id": context["user_id"]}, headers=context["headers"], verify=VERIFY_SSL)
        # Unassign
        resp = requests.post(f"{BASE_URL}/v1/shopping_plans/{temp_plan_id}/unassign", params={"assignee_id": context["user_id"]}, headers=context["headers"], verify=VERIFY_SSL)
        if resp.status_code == 200 and resp.json()["plan_status"] == "created":
            print_success("Unassigned Plan: OK (Status back to CREATED)")
        else:
            print_error(f"Unassign failed: {resp.text}")
        
        # Clean up this plan
        requests.delete(f"{BASE_URL}/v1/shopping_plans/{temp_plan_id}", headers=context["headers"], verify=VERIFY_SSL)

    # === Sub-flow 3: Cancellation Flow (Cancel -> Reopen -> Delete) ===
    print_info("--- Flow 3: Cancellation & Delete Flow ---")
    resp = requests.post(f"{BASE_URL}/v1/shopping_plans/", json=payload, headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 201:
        cancel_plan_id = resp.json()["plan_id"]
        
        # Cancel
        resp = requests.post(f"{BASE_URL}/v1/shopping_plans/{cancel_plan_id}/cancel", params={"assigner_id": context["user_id"]}, headers=context["headers"], verify=VERIFY_SSL)
        if resp.status_code == 200 and resp.json()["plan_status"] == "cancelled":
            print_success("Cancelled Plan: OK")
        
        # Reopen
        resp = requests.post(f"{BASE_URL}/v1/shopping_plans/{cancel_plan_id}/reopen", params={"assigner_id": context["user_id"]}, headers=context["headers"], verify=VERIFY_SSL)
        if resp.status_code == 200 and resp.json()["plan_status"] == "created":
            print_success("Reopened Plan: OK")
            
        # Delete
        resp = requests.delete(f"{BASE_URL}/v1/shopping_plans/{cancel_plan_id}", headers=context["headers"], verify=VERIFY_SSL)
        if resp.status_code == 204:
            print_success("Deleted Plan: OK")
        else:
            print_error(f"Delete Plan failed: {resp.text}")

    # List All Plans
    resp = requests.get(f"{BASE_URL}/v1/shopping_plans/", headers=context["headers"], verify=VERIFY_SSL)
    if resp.status_code == 200:
        print_success(f"List All Plans: OK (Found {len(resp.json()['data'])} items)")

    return True

def cleanup():
    print_info("\n--- 5. CLEANUP ---")
    if context.get("group_id"):
        resp = requests.delete(f"{BASE_URL}/api/v1/user-service/groups/{context['group_id']}", headers=context["headers"], verify=VERIFY_SSL)
        if resp.status_code == 200:
            print_success("Deleted test group and cascading storage data")
        else:
            print_info(f"Cleanup group failed (might already be deleted): {resp.status_code}")

def main():
    if setup_auth_and_group():
        try:
            if test_storage_apis():
                test_storable_unit_apis()
                test_shopping_plan_apis()
            print_info("\n--- ALL TESTS COMPLETED ---")
        except Exception as e:
            print_error(f"Test crashed with error: {e}")
        finally:
            # Always attempt cleanup to avoid cluttering DB
            cleanup()

if __name__ == "__main__":
    main()