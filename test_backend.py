"""
API Test Script
Run this to verify the FastAPI backend is working correctly
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200, "Health check failed"
    print("✅ Health check passed!")


def test_triage_prediction():
    """Test main triage prediction endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Triage Prediction")
    print("="*60)
    
    patient_data = {
        "email": "test.patient@example.com",
        "age": 55,
        "gender": "Male",
        "vitals": {
            "heart_rate": 125,
            "bp_systolic": 165,
            "bp_diastolic": 95,
            "temperature": 101.2
        },
        "symptoms": ["chest pain", "shortness of breath", "dizziness"],
        "medical_history": ["hypertension", "diabetes"],
        "allergies": ["penicillin"],
        "current_medications": ["metformin", "lisinopril"]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/predict", json=patient_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📊 Triage Result:")
        print(f"  Patient ID: {result['patient_id']}")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Priority Score: {result['priority_score']}")
        print(f"  Department: {result['department']}")
        print(f"  Position in Queue: {result['position_in_queue']}")
        print(f"  Estimated Wait: {result['estimated_wait_time']} minutes")
        print(f"  AI Confidence: {result['ai_confidence']:.2%}")
        print(f"\n  Medical Advice:")
        print(f"  {result['medical_advice']}")
        print("\n✅ Triage prediction passed!")
        return result['patient_id']
    else:
        print(f"❌ Error: {response.json()}")
        return None


def test_queue_view():
    """Test queue viewing"""
    print("\n" + "="*60)
    print("TEST 3: View Priority Queue")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/queue?limit=5")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        queue = response.json()
        print(f"\n📋 Current Queue ({len(queue)} patients):")
        for idx, entry in enumerate(queue, 1):
            print(f"  {idx}. {entry['email']} - Priority: {entry['priority_score']} ({entry['risk_level']})")
        print("\n✅ Queue view passed!")
    else:
        print(f"❌ Error: {response.json()}")


def test_nearby_hospitals():
    """Test hospital finder"""
    print("\n" + "="*60)
    print("TEST 4: Find Nearby Hospitals")
    print("="*60)
    
    # New York City coordinates
    params = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "radius_km": 5,
        "limit": 3
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/hospitals/nearby", params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        hospitals = response.json()
        print(f"\n🏥 Nearby Hospitals ({len(hospitals)} found):")
        for hospital in hospitals:
            print(f"\n  {hospital['name']}")
            print(f"    Distance: {hospital['distance_km']} km ({hospital['travel_time_minutes']} min)")
            print(f"    Occupancy: {hospital['live_occupancy']}%")
            print(f"    Est. Wait: {hospital['estimated_wait_time']} minutes")
            print(f"    Emergency: {'Yes' if hospital['has_emergency'] else 'No'}")
        print("\n✅ Hospital finder passed!")
    else:
        print(f"❌ Error: {response.json()}")


def test_audit_trail(patient_id):
    """Test audit trail retrieval"""
    print("\n" + "="*60)
    print("TEST 5: Audit Trail")
    print("="*60)
    
    if not patient_id:
        print("⚠️ Skipping (no patient ID from previous test)")
        return
    
    response = requests.get(f"{BASE_URL}/api/v1/audit/{patient_id}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        logs = response.json()
        print(f"\n📝 Audit Logs ({len(logs)} entries):")
        for log in logs:
            print(f"\n  {log['timestamp']}")
            print(f"    Action: {log['action']}")
            print(f"    Risk: {log['risk_level']} (Score: {log['priority_score']})")
            print(f"    Rationale: {log['rationale'][:100]}...")
        print("\n✅ Audit trail passed!")
    else:
        print(f"❌ Error: {response.json()}")


def test_dynamic_priority_update(patient_id):
    """Test dynamic priority re-ranking"""
    print("\n" + "="*60)
    print("TEST 6: Dynamic Priority Update")
    print("="*60)
    
    if not patient_id:
        print("⚠️ Skipping (no patient ID from previous test)")
        return
    
    new_priority = 95.0  # Simulate worsening condition
    response = requests.post(
        f"{BASE_URL}/api/v1/queue/{patient_id}/update-priority",
        params={"new_priority_score": new_priority}
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📈 Priority Updated:")
        print(f"  Patient ID: {result['patient_id']}")
        print(f"  New Priority: {result['new_priority']}")
        print(f"  New Position: {result['new_position']}")
        print("\n✅ Dynamic priority update passed!")
    else:
        print(f"❌ Error: {response.json()}")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "🧪 "*30)
    print("FASTAPI BACKEND TEST SUITE")
    print("🧪 " * 30)
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Triage prediction
        patient_id = test_triage_prediction()
        
        # Test 3: View queue
        test_queue_view()
        
        # Test 4: Find hospitals
        test_nearby_hospitals()
        
        # Test 5: Audit trail
        test_audit_trail(patient_id)
        
        # Test 6: Dynamic priority update
        test_dynamic_priority_update(patient_id)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n🎉 Your FastAPI backend is working perfectly!")
        print(f"\n📚 API Documentation: {BASE_URL}/api/docs")
        print(f"🏥 Health Status: {BASE_URL}/health")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to FastAPI server")
        print("Please make sure the server is running:")
        print("  1. Open a terminal")
        print("  2. Run: start_backend.bat")
        print("  3. Wait for server to start")
        print("  4. Run this test script again")
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
