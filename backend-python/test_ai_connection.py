"""
Simple AI Connection Test
Tests that Gemini API key works and returns valid responses
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_ai_connection():
    print("🤖 Testing Gemini AI Connection\n")
    
    # Test 1: Health check
    print("1️⃣ Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print(f"   ✅ Backend healthy\n")
    
    # Test 2: Execute algorithm (no AI)
    print("2️⃣ Execute Algorithm (No AI)...")
    response = requests.post(f"{BASE_URL}/execute", json={
        "algorithmId": "bubble_sort",
        "array": [3, 1, 4]
    })
    assert response.status_code == 200
    trace = response.json()["trace"]
    print(f"   ✅ Trace generated: {len(trace)} steps\n")
    
    # Test 3: Get ONE AI explanation (minimal)
    print("3️⃣ Testing AI Explanation (ONE call only)...")
    frame = trace[0]
    
    try:
        response = requests.post(f"{BASE_URL}/explain-step", json={
            "frame": frame,
            "userBehavior": {
                "pauseDuration": 0,
                "replayCount": 0,
                "speedMultiplier": 1.0
            }
        })
        
        if response.status_code == 200:
            explanation = response.json()
            print(f"   ✅ AI Connected!")
            print(f"   Mode: {explanation['mode']}")
            print(f"   Explanation: {explanation['explanation'][:100]}...")
            print(f"\n🎉 Gemini 2.0 Flash working correctly!")
            return True
        else:
            print(f"   ❌ AI request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


if __name__ == "__main__":
    try:
        success = test_ai_connection()
        if success:
            print("\n✅ All systems operational:")
            print("   - Algorithm execution ✓")
            print("   - Gemini AI integration ✓")
            print("   - API key valid ✓")
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
