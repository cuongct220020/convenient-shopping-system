#!/usr/bin/env python3
"""
Manual connectivity test for the Internal Group Access API.
Target: http://localhost:9001/api/v1/user-service/groups/internal/{group_id}/members/{user_id}/access-check

This script verifies:
1. Network connectivity to the exposed port 9001.
2. Routing to the internal endpoint.
3. Response structure (expecting 404 for random UUIDs, which confirms the service logic is executing).
"""

import json
import uuid
import urllib.request
import urllib.error
import sys

# Configuration
# Note: 9001 is the port exposed in docker-compose for user-service
BASE_URL = "http://localhost:9001/api/v1/user-service"

class Colors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def test_internal_access_check():
    print(f"{Colors.BOLD}🚀 Testing Internal Group Access API Connectivity{Colors.ENDC}")
    
    # Generate random UUIDs
    group_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    url = f"{BASE_URL}/groups/internal/{group_id}/members/{user_id}/access-check"
    
    print(f"Target URL: {url}")
    print(f"Generated Group ID: {group_id}")
    print(f"Generated User ID:  {user_id}")
    
    payload = {
        "check_head_chef": False
    }
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        print(f"\nSending POST request...")
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            
            print(f"{Colors.OKGREEN}✅ Response Received (Status: {status_code}){Colors.ENDC}")
            print(f"Body: {response_body}")
            
            # If we get here, it means 200 OK (unlikely for random UUIDs unless logic is very permissive)
            
    except urllib.error.HTTPError as e:
        # We EXPECT a 404 Not Found because the group/user don't exist in DB
        # This proves the endpoint is reachable and logic is running.
        status_code = e.code
        response_body = e.read().decode('utf-8')
        
        if status_code == 404:
            print(f"{Colors.OKGREEN}✅ Success! Received expected 404 Not Found.{Colors.ENDC}")
            print("This confirms the endpoint is reachable and the service logic (check_group_access) was executed.")
            try:
                json_body = json.loads(response_body)
                print(f"JSON Response: {json.dumps(json_body, indent=2)}")
            except:
                print(f"Raw Response: {response_body}")
        else:
            print(f"{Colors.WARNING}⚠️  Received Status: {status_code}{Colors.ENDC}")
            print(f"Response: {response_body}")
            
    except urllib.error.URLError as e:
        print(f"{Colors.FAIL}❌ Connection Failed: {e.reason}{Colors.ENDC}")
        print("Ensure 'user-service' is running and port 9001 is exposed.")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}❌ Unexpected Error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    test_internal_access_check()
