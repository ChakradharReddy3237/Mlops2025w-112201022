#!/usr/bin/env python3
"""
Quick Docker Test - Run this after fixing the artifact reference
"""

import subprocess
import time
import requests

# Test with curl
print("\n" + "="*60)
print("Testing Docker Container with curl")
print("="*60)

def test_curl():
    print("\n1. Testing root endpoint...")
    result = subprocess.run(
        ["curl", "-s", "http://localhost:8080/"],
        capture_output=True, text=True
    )
    print(f"Response: {result.stdout}")
    
    print("\n2. Testing predict endpoint...")
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "-H", "Content-Type: application/json",
        "--data", "[5.1,3.5,1.4,0.2]",
        "http://localhost:8080/predict"
    ], capture_output=True, text=True)
    print(f"Response: {result.stdout}")

# Run tests
try:
    test_curl()
except Exception as e:
    print(f"Error: {e}")
