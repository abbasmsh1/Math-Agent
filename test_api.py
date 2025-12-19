"""
Test script for Math Agent System API
"""
import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"   [OK] Status: {response.status_code}")
        print(f"   [OK] Response: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def test_home_page():
    """Test the home page"""
    print("\n2. Testing / (home page) endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        response.raise_for_status()
        if "Math Agent System" in response.text:
            print(f"   [OK] Status: {response.status_code}")
            print(f"   [OK] Page contains 'Math Agent System'")
            return True
        else:
            print(f"   [ERROR] Page content issue")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def test_upload_endpoint():
    """Test the upload endpoint (without actual file)"""
    print("\n3. Testing /upload endpoint (validation)...")
    try:
        # Test without file - should return 422 (validation error)
        response = requests.post(f"{BASE_URL}/upload", timeout=5)
        if response.status_code == 422:
            print(f"   [OK] Status: {response.status_code} (Expected validation error)")
            return True
        else:
            print(f"   [WARNING] Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def test_solve_endpoint():
    """Test the solve endpoint"""
    print("\n4. Testing /solve endpoint...")
    try:
        test_problem = {
            "text": "What is the probability of rolling a 6 on a fair die?",
            "type": "probability"
        }
        response = requests.post(
            f"{BASE_URL}/solve",
            json=test_problem,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Status: {response.status_code}")
            print(f"   [OK] Solution received")
            print(f"   [OK] Has explanation: {'explanation' in data}")
            print(f"   [OK] Has steps: {'steps' in data}")
            return True
        elif response.status_code == 500:
            error_data = response.json()
            print(f"   [WARNING] Status: {response.status_code}")
            print(f"   [WARNING] Error: {error_data.get('detail', 'Unknown error')}")
            print(f"   [WARNING] This might be due to missing/invalid MISTRAL_API_KEY")
            return False
        else:
            print(f"   [ERROR] Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print(f"   [WARNING] Request timed out (might be normal for AI processing)")
        return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def wait_for_server(max_attempts=10):
    """Wait for the server to be ready"""
    print("Waiting for server to start...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("[OK] Server is ready!\n")
                return True
        except:
            pass
        time.sleep(1)
        print(f"   Attempt {i+1}/{max_attempts}...")
    print("X Server did not start in time")
    return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Math Agent System - API Test Suite")
    print("=" * 50)
    
    if not wait_for_server():
        print("\n[X] Cannot connect to server. Make sure it's running:")
        print("  uvicorn app.main:app --reload")
        sys.exit(1)
    
    results = []
    results.append(("Health Endpoint", test_health_endpoint()))
    results.append(("Home Page", test_home_page()))
    results.append(("Upload Endpoint", test_upload_endpoint()))
    results.append(("Solve Endpoint", test_solve_endpoint()))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

