#!/usr/bin/env python3
import requests
import json
import sys
import time

def test_api(base_url):
    print("🧪 Testing Offer Management API")
    print("=" * 60)
    print(f"Base URL: {base_url}\n")
    
    # Test 1: Get offers for USER001
    print("Test 1: Get personalized offers for USER001")
    print("-" * 60)
    
    response = requests.post(
        f"{base_url}/offers/recommend",
        json={"user_id": "USER001"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Received {len(data['recommended_offers'])} offers")
        for i, offer in enumerate(data['recommended_offers'], 1):
            print(f"  {i}. {offer['offer_name']} ({offer['category']}) - Score: {offer['score']}")
    else:
        print(f"✗ Error: {response.text}")
        return False
    
    print()
    
    # Test 2: Track click event
    print("Test 2: Track click event")
    print("-" * 60)
    
    if response.status_code == 200:
        first_offer = data['recommended_offers'][0]
        
        response = requests.post(
            f"{base_url}/events/track",
            json={
                "user_id": "USER001",
                "offer_id": first_offer['offer_id'],
                "category": first_offer['category'],
                "event_type": "CLICK"
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Event tracked: {data['event_id']}")
        else:
            print(f"✗ Error: {response.text}")
            return False
    
    print()
    
    # Test 3: Get offers for different user
    print("Test 3: Get personalized offers for USER002")
    print("-" * 60)
    
    response = requests.post(
        f"{base_url}/offers/recommend",
        json={"user_id": "USER002"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Received {len(data['recommended_offers'])} offers")
        for i, offer in enumerate(data['recommended_offers'], 1):
            print(f"  {i}. {offer['offer_name']} ({offer['category']}) - Score: {offer['score']}")
    else:
        print(f"✗ Error: {response.text}")
        return False
    
    print()
    print("=" * 60)
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <API_ENDPOINT>")
        print("Example: python test_api.py https://abc123.execute-api.us-east-1.amazonaws.com/prod")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    try:
        success = test_api(base_url)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
