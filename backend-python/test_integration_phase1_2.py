"""
Integration Test: Phase 1 (Core) + Phase 2 (Sessions)
Tests that session system integrates properly with existing algorithm execution
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_phase_1_2_integration():
    print("🔗 Testing Phase 1 + Phase 2 Integration\n")
    print("="*60)
    
    # STEP 1: Create session (Phase 2)
    print("\n📋 STEP 1: Create Session (Phase 2)")
    response = requests.post(f"{BASE_URL}/session/create", json={})
    assert response.status_code == 200
    session = response.json()
    session_id = session["sessionId"]
    print(f"✅ Session ID: {session_id}")
    
    # STEP 2: Execute algorithm (Phase 1 - Original)
    print("\n⚙️ STEP 2: Execute Bubble Sort (Phase 1)")
    response = requests.post(f"{BASE_URL}/execute", json={
        "algorithmId": "bubble_sort",
        "array": [5, 2, 8, 1, 9]
    })
    assert response.status_code == 200
    trace_data = response.json()
    trace = trace_data["trace"]
    print(f"✅ Trace generated: {len(trace)} steps")
    print(f"   First step: {trace[0]}")
    print(f"   Last step: {trace[-1]}")
    
    # STEP 3: Update session with algorithm info (Phase 2)
    print("\n💾 STEP 3: Update Session with Algorithm")
    response = requests.put(f"{BASE_URL}/session/{session_id}", json={
        "currentAlgorithm": "bubble_sort",
        "currentMode": "learn"
    })
    assert response.status_code == 200
    print("✅ Session updated with algorithm: bubble_sort")
    
    # STEP 4: Get AI explanation for first step (Phase 1 - Original)
    print("\n🤖 STEP 4: Get AI Explanation (Phase 1)")
    first_frame = trace[0]
    response = requests.post(f"{BASE_URL}/explain-step", json={
        "frame": first_frame,
        "userBehavior": {
            "pauseDuration": 2,
            "replayCount": 0,
            "speedMultiplier": 1.0
        }
    })
    assert response.status_code == 200
    explanation = response.json()
    print(f"✅ AI Explanation received")
    print(f"   Mode: {explanation['mode']}")
    print(f"   Text: {explanation['explanation'][:80]}...")
    
    # STEP 5: Simulate user understanding a concept (Phase 2)
    print("\n📈 STEP 5: Update Concept Mastery")
    # Simulate user answered questions about comparisons
    response = requests.post(f"{BASE_URL}/concept/update-mastery", json={
        "sessionId": session_id,
        "algorithm": "bubble_sort",
        "concept": "comparisons",
        "performanceData": {
            "correct_answers": 4,
            "total_attempts": 5,
            "time_spent": 60,
            "replays": 1
        }
    })
    assert response.status_code == 200
    mastery = response.json()
    print(f"✅ Concept mastery updated")
    print(f"   Concept: {mastery['concept']}")
    print(f"   New score: {mastery['newScore']}")
    
    # STEP 6: Get mode recommendation based on progress (Phase 2)
    print("\n🎯 STEP 6: Get Mode Recommendation")
    response = requests.post(f"{BASE_URL}/mode/recommend", json={
        "sessionId": session_id,
        "algorithm": "bubble_sort"
    })
    assert response.status_code == 200
    recommendation = response.json()
    print(f"✅ Mode recommended: {recommendation['recommendedMode']}")
    print(f"   Reason: {recommendation['reason']}")
    print(f"   Current mastery: {recommendation['averageMastery']}")
    
    # STEP 7: Execute another algorithm run (Phase 1)
    print("\n⚙️ STEP 7: Execute Another Run")
    response = requests.post(f"{BASE_URL}/execute", json={
        "algorithmId": "bubble_sort",
        "array": [3, 1, 4, 1, 5]  # Different array
    })
    assert response.status_code == 200
    trace2 = response.json()["trace"]
    print(f"✅ Second trace generated: {len(trace2)} steps")
    
    # STEP 8: Update session stats (Phase 2)
    print("\n📊 STEP 8: Update Session Stats")
    response = requests.put(f"{BASE_URL}/session/{session_id}", json={
        "totalTime": 300,  # 5 minutes
        "questionsAnswered": 5,
        "accuracy": 0.8
    })
    assert response.status_code == 200
    print("✅ Session stats updated")
    
    # STEP 9: Get final analytics (Phase 2)
    print("\n📈 STEP 9: Get Session Analytics")
    response = requests.get(f"{BASE_URL}/session/{session_id}/stats")
    assert response.status_code == 200
    analytics = response.json()
    print(f"✅ Analytics retrieved:")
    print(f"   Average mastery: {analytics['averageMastery']}")
    print(f"   Total concepts: {analytics['totalConcepts']}")
    print(f"   Events logged: {analytics['events']}")
    
    # STEP 10: Verify Phase 1 still works independently
    print("\n🔍 STEP 10: Verify Phase 1 Independence")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    health = response.json()
    print(f"✅ Health check: {health['status']}")
    
    print("\n" + "="*60)
    print("🎉 INTEGRATION TEST PASSED!")
    print("="*60)
    print("\n✅ Phase 1 (Core) and Phase 2 (Sessions) are fully integrated")
    print("✅ Algorithm execution works")
    print("✅ AI explanations work")
    print("✅ Session tracking works")
    print("✅ Concept mastery tracking works")
    print("✅ Mode recommendations work")
    print("\n🚀 Ready to proceed to Phase 3!")


if __name__ == "__main__":
    try:
        test_phase_1_2_integration()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Backend not running")
        print("   Start with: uvicorn main:app --reload --port 8000")
    except AssertionError as e:
        print(f"❌ Test failed at assertion: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
