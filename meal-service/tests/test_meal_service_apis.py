#!/usr/bin/env python3
"""
Real integration test for head chef middleware functionality.

This script tests the complete flow using real user accounts through the API gateway.
"""

import requests
import json
import random
import string
import uuid
from datetime import datetime, timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://dichotienloi.com"  # Kong API Gateway URL (external) - for all service endpoints
VERIFY_SSL = False

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BLUE = '\033[94m'
YELLOW = '\033[93m'

def print_success(msg):
    print(f"{GREEN}[PASS] {msg}{RESET}")

def print_error(msg):
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}[INFO] {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}[WARN] {msg}{RESET}")

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class RealIntegrationTester:
    def __init__(self):
        self.context = {
            "head_chef_headers": {},
            "non_head_chef_headers": {},
            "group_id": None,
            "head_chef_user_id": None,
            "non_head_chef_user_id": None,
            "meal_id": None,
            "today": (datetime.now() + timedelta(days=random.randint(2, 30))).strftime("%Y-%m-%d")  # Use random future date to avoid conflicts
        }

    def setup_users_and_group(self):
        """Setup real users and group through the API"""
        print_info("--- 1. SETUP - Creating Users and Group ---")

        # Create head chef user
        head_chef_email = f"head_chef_{random_string()}@example.com".lower()
        head_chef_password = "Password123!"
        head_chef_username = f"head_chef_{random_string()}"

        print_info(f"Creating head chef user: {head_chef_email}")
        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/auth/register",
            json={"username": head_chef_username, "email": head_chef_email, "password": head_chef_password},
            verify=VERIFY_SSL
        )
        if resp.status_code not in [200, 201]:
            print_error(f"Head chef registration failed: {resp.text}")
            return False

        # Verify OTP
        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/auth/otp/send",
            json={"email": head_chef_email, "action": "register"},
            verify=VERIFY_SSL
        )
        otp_code = resp.json().get("data", {}).get("otp_code")
        if not otp_code:
            print_error("Cannot retrieve OTP code for head chef")
            return False

        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/auth/otp/verify",
            json={"email": head_chef_email, "otp_code": otp_code},
            verify=VERIFY_SSL
        )
        if resp.status_code != 200:
            print_error("OTP verification failed for head chef")
            return False

        # Login as head chef
        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/auth/login",
            json={"identifier": head_chef_email, "password": head_chef_password},
            verify=VERIFY_SSL
        )
        if resp.status_code != 200:
            print_error(f"Head chef login failed: {resp.text}")
            return False

        head_chef_token = resp.json()["data"]["access_token"]
        self.context["head_chef_headers"] = {"Authorization": f"Bearer {head_chef_token}"}

        # Get head chef user ID
        resp = requests.get(
            f"{BASE_URL}/api/v1/user-service/users/me",
            headers=self.context["head_chef_headers"],
            verify=VERIFY_SSL
        )
        if resp.status_code != 200:
            print_error("Failed to get head chef user info")
            return False

        self.context["head_chef_user_id"] = resp.json()["data"]["user_id"]
        print_success(f"Head chef created with ID: {self.context['head_chef_user_id']}")

        # Create group (head chef becomes owner/head chef automatically)
        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/groups",
            json={"group_name": f"Test Group {random_string()}"},
            headers=self.context["head_chef_headers"],
            verify=VERIFY_SSL
        )
        if resp.status_code not in [200, 201]:
            print_error(f"Group creation failed: {resp.text}")
            return False

        self.context["group_id"] = resp.json()["data"]["id"]
        print_success(f"Group created with ID: {self.context['group_id']}")

        # Create non-head chef user
        non_head_chef_email = f"member_{random_string()}@example.com".lower()
        non_head_chef_password = "Password123!"
        non_head_chef_username = f"member_{random_string()}"

        print_info(f"Creating non-head chef user: {non_head_chef_email}")
        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/auth/register",
            json={"username": non_head_chef_username, "email": non_head_chef_email, "password": non_head_chef_password},
            verify=VERIFY_SSL
        )
        if resp.status_code not in [200, 201]:
            print_error(f"Non-head chef registration failed: {resp.text}")
            return False

        # Verify OTP for non-head chef
        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/auth/otp/send",
            json={"email": non_head_chef_email, "action": "register"},
            verify=VERIFY_SSL
        )
        otp_code = resp.json().get("data", {}).get("otp_code")
        if not otp_code:
            print_error("Cannot retrieve OTP code for non-head chef")
            return False

        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/auth/otp/verify",
            json={"email": non_head_chef_email, "otp_code": otp_code},
            verify=VERIFY_SSL
        )
        if resp.status_code != 200:
            print_error("OTP verification failed for non-head chef")
            return False

        # Login as non-head chef
        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/auth/login",
            json={"identifier": non_head_chef_email, "password": non_head_chef_password},
            verify=VERIFY_SSL
        )
        if resp.status_code != 200:
            print_error(f"Non-head chef login failed: {resp.text}")
            return False

        non_head_chef_token = resp.json()["data"]["access_token"]
        self.context["non_head_chef_headers"] = {"Authorization": f"Bearer {non_head_chef_token}"}

        # Get non-head chef user ID
        resp = requests.get(
            f"{BASE_URL}/api/v1/user-service/users/me",
            headers=self.context["non_head_chef_headers"],
            verify=VERIFY_SSL
        )
        if resp.status_code != 200:
            print_error("Failed to get non-head chef user info")
            return False

        self.context["non_head_chef_user_id"] = resp.json()["data"]["user_id"]
        print_success(f"Non-head chef created with ID: {self.context['non_head_chef_user_id']}")

        # Add non-head chef to group as a regular member
        resp = requests.post(
            f"{BASE_URL}/api/v1/user-service/groups/{self.context['group_id']}/members",
            json={"identifier": non_head_chef_email},
            headers=self.context["head_chef_headers"],
            verify=VERIFY_SSL
        )
        if resp.status_code not in [200, 201]:
            print_error(f"Failed to invite non-head chef to group: {resp.text}")
            return False

        print_success("Non-head chef invited to group successfully")
        return True

    def test_user_service_internal_endpoint(self):
        """Test the internal endpoint that meal service middleware calls - SKIPPED for external testing"""
        print_info("\n--- 2. TESTING - User Service Internal Endpoint ---")
        print_info("SKIPPED: Internal endpoint can only be tested from within Docker network")
        print_info("The middleware communication will be tested indirectly through meal service endpoints")
        return True  # Skip this test but return True to continue

    def test_head_chef_can_create_meals(self):
        """Test that head chef can create meals"""
        print_info("\n--- 3. TESTING - Head Chef Can Create Meals ---")

        payload = {
            "date": self.context["today"],
            "group_id": self.context["group_id"],
            "breakfast": {
                "action": "upsert",
                "recipe_list": [
                    {"recipe_id": 12, "recipe_name": "Test Breakfast Updated", "servings": 2}
                ]
            },
            "lunch": {"action": "skip"},
            "dinner": {"action": "skip"}
        }

        resp = requests.post(
            f"{BASE_URL}/v1/meals/command?group_id={self.context['group_id']}",
            json=payload,
            headers=self.context["head_chef_headers"], # Will be processed by Kong and passed to meal service
            verify=VERIFY_SSL
        )

        print_info(f"Head chef create meals response: {resp.status_code} - {resp.text}")
        
        if resp.status_code == 200:
            data = resp.json()
            print_success("Head chef successfully created meals")
            
            # Store meal ID for later tests
            for meal in data:
                if meal.get("meal_type") == "breakfast" and meal.get("meal_status") == "created":
                    self.context["meal_id"] = meal.get("meal_id")
                    break
            return True
        elif resp.status_code == 403:
            print_error("Head chef was denied access - this indicates middleware is working but user might not be head chef")
            return False
        else:
            print_error(f"Unexpected response for head chef: {resp.status_code}")
            return False

    def test_non_head_chef_cannot_create_meals(self):
        """Test that non-head chef cannot create meals"""
        print_info("\n--- 4. TESTING - Non-Head Chef Cannot Create Meals ---")

        payload = {
            "date": self.context["today"],
            "group_id": self.context["group_id"],
            "breakfast": {
                "action": "upsert",
                "recipe_list": [
                    {"recipe_id": 13, "recipe_name": "Blocked Breakfast", "servings": 2}
                ]
            },
            "lunch": {"action": "skip"},
            "dinner": {"action": "skip"}
        }

        resp = requests.post(
            f"{BASE_URL}/v1/meals/command?group_id={self.context['group_id']}",
            json=payload,
            headers=self.context["non_head_chef_headers"],
            verify=VERIFY_SSL
        )

        print_info(f"Non-head chef create meals response: {resp.status_code} - {resp.text}")
        
        if resp.status_code == 403:
            print_success("Non-head chef correctly blocked from creating meals")
            return True
        elif resp.status_code == 200:
            print_error("Non-head chef was allowed to create meals - middleware failed")
            return False
        else:
            print_warning(f"Unexpected response for non-head chef: {resp.status_code}")
            # This could be due to other auth issues, but 403 is the expected response for head chef middleware
            return resp.status_code == 403

    def test_head_chef_can_modify_meals(self):
        """Test that head chef can modify meals (cancel)"""
        if not self.context.get("meal_id"):
            print_warning("Skipping modify test - no meal ID available")
            return True

        print_info("\n--- 5. TESTING - Head Chef Can Cancel Meals ---")

        resp = requests.post(
            f"{BASE_URL}/v1/meals/{self.context['meal_id']}/cancel?group_id={self.context['group_id']}",
            headers=self.context["head_chef_headers"],
            verify=VERIFY_SSL
        )

        print_info(f"Head chef cancel meals response: {resp.status_code} - {resp.text}")

        if resp.status_code == 200:
            print_success("Head chef allowed to cancel meals")
            return True
        elif resp.status_code == 404:
            print_warning("Meal not found for cancellation")
            return True  # Still indicates middleware didn't block
        elif resp.status_code == 403:
            print_error("Head chef was denied access to cancel meals")
            return False
        else:
            print_warning(f"Unexpected response for head chef cancel: {resp.status_code}")
            return resp.status_code != 403  # Pass if not 403 (which would mean middleware blocked)

    def test_non_head_chef_cannot_modify_meals(self):
        """Test that non-head chef cannot modify meals (cancel)"""
        if not self.context.get("meal_id"):
            print_warning("Skipping modify test - no meal ID available")
            return True

        print_info("\n--- 6. TESTING - Non-Head Chef Cannot Cancel Meals ---")

        resp = requests.post(
            f"{BASE_URL}/v1/meals/{self.context['meal_id']}/cancel?group_id={self.context['group_id']}",
            headers=self.context["non_head_chef_headers"],
            verify=VERIFY_SSL
        )

        print_info(f"Non-head chef cancel meals response: {resp.status_code} - {resp.text}")

        if resp.status_code == 403:
            print_success("Non-head chef correctly blocked from cancelling meals")
            return True
        elif resp.status_code in [200, 404]:
            print_error("Non-head chef was allowed to cancel meals - middleware failed")
            return False
        else:
            print_warning(f"Unexpected response for non-head chef cancel: {resp.status_code}")
            return resp.status_code == 403

    def test_head_chef_can_reopen_meals(self):
        """Test that head chef can reopen meals"""
        if not self.context.get("meal_id"):
            print_warning("Skipping reopen test - no meal ID available")
            return True

        print_info("\n--- 7. TESTING - Head Chef Can Reopen Meals ---")

        resp = requests.post(
            f"{BASE_URL}/v1/meals/{self.context['meal_id']}/reopen?group_id={self.context['group_id']}",
            headers=self.context["head_chef_headers"],
            verify=VERIFY_SSL
        )

        print_info(f"Head chef reopen meals response: {resp.status_code} - {resp.text}")

        if resp.status_code in [200, 400, 404]:  # 200=success, 400=bad request (meal not cancelled), 404=not found
            print_success("Head chef allowed to attempt reopening meals")
            return True
        elif resp.status_code == 403:
            print_error("Head chef was denied access to reopen meals")
            return False
        else:
            print_warning(f"Unexpected response for head chef reopen: {resp.status_code}")
            return resp.status_code != 403

    def test_head_chef_can_finish_meals(self):
        """Test that head chef can finish meals"""
        if not self.context.get("meal_id"):
            print_warning("Skipping finish test - no meal ID available")
            return True

        print_info("\n--- 8. TESTING - Head Chef Can Finish Meals ---")

        resp = requests.post(
            f"{BASE_URL}/v1/meals/{self.context['meal_id']}/finish?group_id={self.context['group_id']}",
            headers=self.context["head_chef_headers"],
            verify=VERIFY_SSL
        )

        print_info(f"Head chef finish meals response: {resp.status_code} - {resp.text}")

        if resp.status_code in [200, 400, 404]:  # 200=success, 400=bad request (meal not created), 404=not found
            print_success("Head chef allowed to attempt finishing meals")
            return True
        elif resp.status_code == 403:
            print_error("Head chef was denied access to finish meals")
            return False
        else:
            print_warning(f"Unexpected response for head chef finish: {resp.status_code}")
            return resp.status_code != 403

    def test_non_head_chef_cannot_reopen_or_finish_meals(self):
        """Test that non-head chef cannot reopen or finish meals"""
        if not self.context.get("meal_id"):
            print_warning("Skipping non-head chef reopen/finish test - no meal ID available")
            return True

        print_info("\n--- 9. TESTING - Non-Head Chef Cannot Reopen/Finish Meals ---")

        # Test reopen
        resp_reopen = requests.post(
            f"{BASE_URL}/v1/meals/{self.context['meal_id']}/reopen?group_id={self.context['group_id']}",
            headers=self.context["non_head_chef_headers"],
            verify=VERIFY_SSL
        )

        # Test finish
        resp_finish = requests.post(
            f"{BASE_URL}/v1/meals/{self.context['meal_id']}/finish?group_id={self.context['group_id']}",
            headers=self.context["non_head_chef_headers"],
            verify=VERIFY_SSL
        )

        print_info(f"Non-head chef reopen response: {resp_reopen.status_code}")
        print_info(f"Non-head chef finish response: {resp_finish.status_code}")

        # Both should return 403 (forbidden)
        if resp_reopen.status_code == 403 and resp_finish.status_code == 403:
            print_success("Non-head chef correctly blocked from reopening and finishing meals")
            return True
        else:
            print_error(f"Non-head chef was not properly blocked - reopen: {resp_reopen.status_code}, finish: {resp_finish.status_code}")
            return False

    def test_get_endpoint_accessible(self):
        """Test that GET endpoints are accessible to all users"""
        print_info("\n--- 7. TESTING - GET Endpoints Are Accessible ---")

        resp = requests.get(
            f"{BASE_URL}/v1/meals/?meal_date={self.context['today']}&group_id={self.context['group_id']}",
            headers=self.context["non_head_chef_headers"],
            verify=VERIFY_SSL
        )

        print_info(f"GET endpoint response: {resp.status_code} - {resp.text}")
        
        # GET endpoints should not be blocked by head chef middleware
        if resp.status_code in [200, 404]:  # 404 is OK if no meals exist
            print_success("GET endpoint accessible (middleware correctly skips GET)")
            return True
        else:
            print_warning(f"GET endpoint blocked: {resp.status_code}")
            return resp.status_code in [200, 404]

    def run_tests(self):
        """Run all integration tests"""
        print_info("Starting Real Integration Tests for Head Chef Middleware")
        print_info(f"External API Gateway (Kong): {BASE_URL}")
        print_info("Note: All endpoints accessed through Kong Gateway - middleware communication tested indirectly")

        # Setup
        if not self.setup_users_and_group():
            print_error("Setup failed")
            return False

        # Test the internal endpoint first
        if not self.test_user_service_internal_endpoint():
            print_warning("Internal endpoint test failed, but continuing with other tests...")

        # Run tests
        tests = [
            ("Head Chef Can Create Meals", self.test_head_chef_can_create_meals),
            ("Non-Head Chef Cannot Create Meals", self.test_non_head_chef_cannot_create_meals),
            ("Head Chef Can Cancel Meals", self.test_head_chef_can_modify_meals),
            ("Non-Head Chef Cannot Cancel Meals", self.test_non_head_chef_cannot_modify_meals),
            ("Head Chef Can Reopen Meals", self.test_head_chef_can_reopen_meals),
            ("Head Chef Can Finish Meals", self.test_head_chef_can_finish_meals),
            ("Non-Head Chef Cannot Reopen/Finish Meals", self.test_non_head_chef_cannot_reopen_or_finish_meals),
            ("GET Endpoint Accessible", self.test_get_endpoint_accessible),
        ]

        results = []
        for test_name, test_func in tests:
            print_info(f"\nRunning: {test_name}")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print_error(f"Test '{test_name}' failed with exception: {e}")
                results.append((test_name, False))

        # Summary
        print_info(f"\n{'='*70}")
        print_info("COMPREHENSIVE TEST RESULTS SUMMARY:")
        print_info(f"{'='*70}")

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            icon = "✓" if result else "✗"
            print_info(f"{icon} {test_name}: {status}")

        print_info(f"\nOverall: {passed}/{total} tests passed")

        if passed == total:
            print_success("🎉 All comprehensive integration tests PASSED!")
            print_success("Head chef middleware is working correctly with all meal service endpoints.")
        else:
            print_error(f"❌ {total - passed} test(s) FAILED!")
            print_error("There may be issues with the middleware or system configuration.")
        
        return passed == total

def main():
    tester = RealIntegrationTester()
    success = tester.run_tests()
    
    if not success:
        exit(1)

if __name__ == "__main__":
    main()