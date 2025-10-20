#!/usr/bin/env python3
"""
FastAPI Testing Script - Test the API before and after Dockerization
"""

import requests
import json
import time
import sys

def test_api(base_url="http://localhost:8080"):
    """Test the FastAPI endpoints"""
    
    print("\n" + "="*60)
    print("Testing FastAPI Endpoints")
    print("="*60)
    
    try:
        # Test root endpoint
        print("\n1. Testing root endpoint (GET /)...")
        response = requests.get(f"{base_url}/", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"   ✓ Status: {response.status_code}")
        print(f"   ✓ Response: {json.dumps(data, indent=2)}")
        
        # Test predict endpoint
        print("\n2. Testing predict endpoint (POST /predict)...")
        
        # Test samples
        test_samples = [
            {"data": [5.1, 3.5, 1.4, 0.2], "expected": "Setosa (class 0)"},
            {"data": [6.7, 3.0, 5.2, 2.3], "expected": "Virginica (class 2)"},
            {"data": [5.9, 3.0, 4.2, 1.5], "expected": "Versicolor (class 1)"},
        ]
        
        iris_names = ["Setosa", "Versicolor", "Virginica"]
        
        for i, sample in enumerate(test_samples, 1):
            print(f"\n   Sample {i}: {sample['data']}")
            response = requests.post(
                f"{base_url}/predict",
                json=sample['data'],
                timeout=5
            )
            response.raise_for_status()
            result = response.json()
            prediction = result.get('prediction')
            
            print(f"   ✓ Prediction: {prediction} ({iris_names[prediction]})")
            print(f"   ✓ Expected: {sample['expected']}")
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n✗ ERROR: Cannot connect to {base_url}")
        print("  Make sure the server is running!")
        print(f"  Start it with: uvicorn app.main:app --host 0.0.0.0 --port 8080")
        return False
        
    except requests.exceptions.Timeout:
        print(f"\n✗ ERROR: Request timed out")
        print("  The server might be starting up. Wait a moment and try again.")
        return False
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False


def wait_for_server(base_url="http://localhost:8080", max_attempts=30):
    """Wait for server to be ready"""
    print(f"\nWaiting for server at {base_url}...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/", timeout=1)
            if response.status_code == 200:
                print(f"✓ Server is ready after {attempt + 1} seconds!")
                return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            print(f"  Attempt {attempt + 1}/{max_attempts}...", end='\r')
            time.sleep(1)
    
    print(f"\n✗ Server did not become ready after {max_attempts} seconds")
    return False


if __name__ == "__main__":
    # Parse command line arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    
    # Check if we should wait for server
    if "--wait" in sys.argv:
        if not wait_for_server(base_url):
            sys.exit(1)
    
    # Run tests
    success = test_api(base_url)
    sys.exit(0 if success else 1)
