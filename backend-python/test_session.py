"""
Test script for Session Management System
Tests session creation, updates, concept tracking, and mode recommendations
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_session_system():
    print("🧪 Testing Session Management System\n")
    
    # Test 1: Create session
    print("1️⃣ Creating new session...")
    response = requests.post(f"{BASE_URL}/session/create", json={})
    assert response.status_code == 200
    session_data = response.json()
    session_id = session_data["sessionId"]
    print(f"   ✅ Session created: {session_id}")
    print(f"   Mode: {session_data['mode']}, Level: {session_data['difficultyLevel']}\n")
    
    # Test 2: Get session
    print("2️⃣ Retrieving session...")
    response = requests.get(f"{BASE_URL}/session/{session_id}")
    assert response.status_code == 200
    session = response.json()
    print(f"   ✅ Session retrieved")
    print(f"   Stats: {session['stats']}\n")
    
    # Test 3: Get mode recommendation
    print("3️⃣ Getting mode recommendation...")
    response = requests.post(f"{BASE_URL}/mode/recommend", json={
        "sessionId": session_id,
        "algorithm": "bubble_sort"
    })
    assert response.status_code == 200
    recommendation = response.json()
    print(f"   ✅ Recommended mode: {recommendation['recommendedMode']}")
    print(f"   Reason: {recommendation['reason']}")
    print(f"   Average mastery: {recommendation['averageMastery']}\n")
    
    # Test 4: Check mode access
    print("4️⃣ Checking mode access...")
    for mode in ["learn", "practice", "challenge"]:
        response = requests.post(f"{BASE_URL}/mode/check-access", json={
            "sessionId": session_id,
            "algorithm": "bubble_sort",
            "mode": mode
        })
        access = response.json()
        status = "✅" if access["canAccess"] else "❌"
        print(f"   {status} {mode}: {access['reason']}")
    print()
    
    # Test 5: Update concept mastery
    print("5️⃣ Updating concept mastery...")
    performance = {
        "correct_answers": 3,
        "total_attempts": 4,
        "time_spent": 120,
        "replays": 0
    }
    
    for concept in ["comparisons", "swaps", "nested_loops"]:
        response = requests.post(f"{BASE_URL}/concept/update-mastery", json={
            "sessionId": session_id,
            "algorithm": "bubble_sort",
            "concept": concept,
            "performanceData": performance
        })
        assert response.status_code == 200
        result = response.json()
        print(f"   ✅ {concept}: {result['newScore']}")
    print()
    
    # Test 6: Get weak areas
    print("6️⃣ Getting weak concepts...")
    response = requests.post(f"{BASE_URL}/concept/weak-areas", json={
        "sessionId": session_id,
        "algorithm": "bubble_sort",
        "threshold": 0.5
    })
    weak_areas = response.json()
    print(f"   Weak concepts: {[c['concept'] for c in weak_areas['weakConcepts']]}")
    print(f"   Recommended focus: {weak_areas['recommendedFocus']}\n")
    
    # Test 7: Update session progress
    print("7️⃣ Updating session progress...")
    response = requests.put(f"{BASE_URL}/session/{session_id}", json={
        "currentMode": "practice",
        "currentAlgorithm": "bubble_sort",
        "totalTime": 300,
        "questionsAnswered": 5,
        "accuracy": 0.8
    })
    assert response.status_code == 200
    print(f"   ✅ Session updated\n")
    
    # Test 8: Get updated recommendation
    print("8️⃣ Getting updated mode recommendation...")
    response = requests.post(f"{BASE_URL}/mode/recommend", json={
        "sessionId": session_id,
        "algorithm": "bubble_sort"
    })
    recommendation = response.json()
    print(f"   ✅ New recommended mode: {recommendation['recommendedMode']}")
    print(f"   Average mastery: {recommendation['averageMastery']}\n")
    
    # Test 9: Get analytics
    print("9️⃣ Getting session analytics...")
    response = requests.get(f"{BASE_URL}/session/{session_id}/stats")
    analytics = response.json()
    print(f"   ✅ Analytics retrieved")
    print(f"   Average mastery: {analytics['averageMastery']}")
    print(f"   Total concepts: {analytics['totalConcepts']}")
    print(f"   Events: {analytics['events']}\n")
    
    print("🎉 All tests passed!")
    return session_id


if __name__ == "__main__":
    try:
        test_session_system()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Backend not running")
        print("   Start with: cd backend-python && uvicorn main:app --reload --port 8000")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
