#!/usr/bin/env python3
"""
Automated test runner for admin API tests through Kong gateway.

This script:
1. Checks if required services are running (PostgreSQL, Redis, Kafka, Kong Gateway)
2. Starts the user service
3. Runs the admin API tests through the Kong gateway
4. Provides detailed reporting of test results
"""

import subprocess
import sys
import time
import requests
import os
import signal
from pathlib import Path
import psutil
import asyncio
import httpx


def check_service_health(url, service_name, timeout=5):
    """Check if a service is running by making a request to its health endpoint"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code in [200, 404, 405]:  # Various valid responses from services
            print(f"✓ {service_name} is accessible at {url}")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print(f"✗ {service_name} is not accessible at {url}")
    return False


def check_port_open(port):
    """Check if a port is open"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def start_user_service():
    """Start the user service in the background"""
    print("Starting user service...")
    
    # Change to user service directory
    os.chdir(Path(__file__).parent.parent)
    
    # Start the user service using the run.py file
    process = subprocess.Popen(
        [sys.executable, "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "APP_HOST": "0.0.0.0", "APP_PORT": "9000", "DEBUG": "True"}
    )
    
    # Wait a bit for the service to start
    time.sleep(5)
    
    # Check if the process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"User service failed to start:")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return None
    
    print("User service started successfully")
    return process


def wait_for_services():
    """Wait for all required services to be ready"""
    print("Waiting for services to be ready...")
    
    max_wait_time = 60  # 60 seconds max wait
    wait_interval = 2
    elapsed = 0
    
    while elapsed < max_wait_time:
        # Check if Kong gateway is running (port 8000)
        kong_ready = check_port_open(8000)
        
        # Check if user service is running (port 9000) - this is where Kong forwards to
        user_service_ready = check_port_open(9000)
        
        if kong_ready and user_service_ready:
            print("All services are ready!")
            return True
        
        print(f"Waiting... ({elapsed}/{max_wait_time}s)")
        time.sleep(wait_interval)
        elapsed += wait_interval
    
    print("Timeout waiting for services to be ready")
    return False


def run_tests():
    """Run the admin API tests"""
    print("Running admin API tests through Kong gateway...")
    
    # Change to user service directory
    os.chdir(Path(__file__).parent.parent)
    
    # Run pytest with specific test file
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/integration/test_admin_apis.py", 
        "-v", 
        "--tb=short"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    
    return result.returncode == 0


def main():
    """Main function to orchestrate the test run"""
    print("🚀 Starting automated admin API tests through Kong gateway")
    print("="*60)
    
    # Check if Kong gateway is running
    print("\n🔍 Checking Kong gateway...")
    if not check_port_open(8000):
        print("❌ Kong gateway is not running on port 8000")
        print("Please start Kong gateway using: docker-compose up kong-gateway")
        return False
    
    # Check if user service is running
    print("\n🔍 Checking user service...")
    user_service_running = check_port_open(9000)
    
    user_service_process = None
    if not user_service_running:
        print("\n📦 Starting user service...")
        user_service_process = start_user_service()
        if not user_service_process:
            print("❌ Failed to start user service")
            return False
    else:
        print("✓ User service is already running on port 9000")
    
    # Wait for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    if not wait_for_services():
        print("❌ Services are not ready. Exiting.")
        if user_service_process:
            user_service_process.terminate()
        return False
    
    # Verify Kong gateway can route to user service
    print("\n🔍 Verifying Kong gateway routing...")
    try:
        with httpx.Client(base_url="http://localhost:8000", timeout=10.0) as client:
            # Try to access a public endpoint to verify Kong is routing properly
            response = client.get("/api/v1/user-service/health", timeout=10.0)
            print(f"✓ Kong gateway routing test: Status {response.status_code}")
    except Exception as e:
        print(f"⚠ Kong gateway routing test failed: {e}")
        print("This might be OK if the health endpoint doesn't exist, continuing with tests...")
    
    # Run the tests
    print("\n🧪 Running admin API tests...")
    tests_passed = run_tests()
    
    # Cleanup
    if user_service_process:
        print("\n🧹 Stopping user service...")
        user_service_process.terminate()
        try:
            user_service_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            user_service_process.kill()
    
    print("\n" + "="*60)
    if tests_passed:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)