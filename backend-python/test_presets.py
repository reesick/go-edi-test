"""
Test Presets - Verify preset management works
"""
import requests

BASE_URL = "http://localhost:8000"

def test_presets():
    print("📚 Testing Preset Management\n")
    
    # Test 1: List all presets
    print("1️⃣ Listing all presets...")
    response = requests.get(f"{BASE_URL}/presets")
    assert response.status_code == 200
    data = response.json()
    presets = data["presets"]
    print(f"   ✅ Found {data['count']} presets")
    for p in presets:
        print(f"      - {p['name']} ({p['difficulty']})")
    
    # Test 2: Get specific presets
    print("\n2️⃣ Loading preset codes...")
    for preset in presets:
        response = requests.get(f"{BASE_URL}/preset/{preset['id']}")
        assert response.status_code == 200
        code = response.json()
        print(f"   ✅ {code['name']}: {len(code['code'])} characters")
    
    print("\n🎉 ALL PRESET TESTS PASSED!")
    return True

if __name__ == "__main__":
    try:
        test_presets()
    except Exception as e:
        print(f"❌ Error: {e}")
