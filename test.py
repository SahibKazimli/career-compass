import requests
import time

BASE_URL = "http://localhost:8000"

# Use timestamp to make email unique
timestamp = int(time.time())
email = f"test{timestamp}@example.com"

# Test 1: Create user
print("Creating user...")
response = requests.post(f"{BASE_URL}/users", params={"email": email, "name": "Test User"})
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✓ User created: {data}\n")
    user_id = data["id"]
    
    # Test 2: Get user
    print(f"Getting user {user_id}...")
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ User retrieved: {response.json()}\n")
    else:
        print(f"✗ Error: {response.text}")
else:
    print(f"✗ Error creating user")
    print(f"Response: {response.text}")
    # Check server terminal for full error details