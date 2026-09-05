import sys
import io
import json
import urllib.request

# Ensure UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def post_json(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_json(endpoint):
    url = f"{BASE_URL}{endpoint}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

def test_ai_assistant_flights():
    data = post_json("/api/v1/ai/assistant/chat", {
        "message": "Find cheapest flights from Hyderabad to Delhi",
        "language": "en"
    })
    assert data["intent"] == "flight_search", f"Expected flight_search, got {data['intent']}"
    assert "HYD" in data["reply"] and "DEL" in data["reply"]
    assert data["action"]["type"] == "populate_search"
    print("[PASS] AI Assistant English Flight Search")

def test_ai_assistant_refund():
    data = post_json("/api/v1/ai/assistant/chat", {
        "message": "What is the status of my refund for PNR AIRX789?",
        "language": "en"
    })
    assert data["intent"] == "refund_tracking", f"Expected refund_tracking, got {data['intent']}"
    assert "AIRX789" in data["reply"]
    assert data["action"]["type"] == "track_refund"
    assert len(data["cards"]) > 0
    print("[PASS] AI Assistant PNR Refund Lookup")

def test_ai_assistant_prediction():
    data = post_json("/api/v1/ai/assistant/chat", {
        "message": "Will airfares surge or should I buy now for Mumbai?",
        "language": "en"
    })
    assert data["intent"] == "price_prediction", f"Expected price_prediction, got {data['intent']}"
    assert "BUY NOW" in data["reply"] or "WAIT" in data["reply"]
    print("[PASS] AI Assistant Price Prediction")

def test_ai_assistant_dgca():
    data = post_json("/api/v1/ai/assistant/chat", {
        "message": "Explain DGCA cancellation rules and delay compensation",
        "language": "en"
    })
    assert data["intent"] == "dgca_policy", f"Expected dgca_policy, got {data['intent']}"
    assert "24-Hour" in data["reply"]
    print("[PASS] AI Assistant DGCA Rules")

def test_ai_assistant_hindi():
    data = post_json("/api/v1/ai/assistant/chat", {
        "message": "पीएनआर AIRX789 का रिफंड कब तक मिलेगा?",
        "language": "hi"
    })
    assert data["intent"] == "refund_tracking"
    assert "AIRX789" in data["reply"]
    assert "रिफंड" in data["reply"]
    print("[PASS] AI Assistant Hindi Multilingual Response")

def test_ai_assistant_telugu():
    data = post_json("/api/v1/ai/assistant/chat", {
        "message": "హైదరాబాద్ నుండి ఢిల్లీ విమాన ధరలు తగ్గుతాయా?",
        "language": "te"
    })
    assert data["intent"] in ["price_prediction", "flight_search"]
    print("[PASS] AI Assistant Telugu Multilingual Response")

def test_ai_assistant_tamil():
    data = post_json("/api/v1/ai/assistant/chat", {
        "message": "டிஜிசிஏ ரத்து விதிகள் என்ன?",
        "language": "ta"
    })
    assert data["intent"] == "dgca_policy"
    print("[PASS] AI Assistant Tamil Multilingual Response")

def test_ai_assistant_marathi():
    data = post_json("/api/v1/ai/assistant/chat", {
        "message": "मुंबईसाठी सर्वात स्वस्त उड्डाणे शोधा",
        "language": "mr"
    })
    assert data["intent"] in ["flight_search", "price_prediction"]
    print("[PASS] AI Assistant Marathi Multilingual Response")

def test_ai_assistant_bengali():
    data = post_json("/api/v1/ai/assistant/chat", {
        "message": "দিল্লির জন্য সবচেয়ে সস্তা ফ্লাইট কোনটি?",
        "language": "bn"
    })
    assert data["intent"] in ["flight_search", "price_prediction"]
    print("[PASS] AI Assistant Bengali Multilingual Response")

if __name__ == "__main__":
    print("Testing AirfareX AI Assistant & Multilingual Endpoints...")
    test_ai_assistant_flights()
    test_ai_assistant_refund()
    test_ai_assistant_prediction()
    test_ai_assistant_dgca()
    test_ai_assistant_hindi()
    test_ai_assistant_telugu()
    test_ai_assistant_tamil()
    test_ai_assistant_marathi()
    test_ai_assistant_bengali()
    print("\nALL 9 AI ASSISTANT & MULTILINGUAL TESTS PASSED!")
