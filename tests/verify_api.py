import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("APP_API_KEY")

def print_result(name, result, error=None):
    if result:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name} - {error}")

def test_health():
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            print_result("Health Check", True)
        else:
            print_result("Health Check", False, f"Status {r.status_code}")
    except Exception as e:
        print_result("Health Check", False, str(e))

def test_ingest_no_auth():
    try:
        r = requests.post(f"{BASE_URL}/ingest/text", json={"text": "test", "sessionId": "test"})
        if r.status_code == 403 or r.status_code == 401:
            print_result("Ingest No Auth (Forbidden)", True)
        else:
            print_result("Ingest No Auth (Forbidden)", False, f"Status {r.status_code} - Should be 403")
    except Exception as e:
        print_result("Ingest No Auth", False, str(e))

def test_ingest_auth():
    try:
        headers = {"X-API-Key": API_KEY}
        # Add a mock email to ensure extraction works
        payload = {
            "text": "CANDIDATE: John Doe\nEmail: test@example.com\nExperience: 5 years in Python.",
            "sessionId": "test-session"
        }
        r = requests.post(f"{BASE_URL}/ingest/text", json=payload, headers=headers)
        if r.status_code == 200:
            print_result("Ingest Auth", True)
        else:
            print_result("Ingest Auth", False, f"Status {r.status_code} - {r.text}")
    except Exception as e:
        print_result("Ingest Auth", False, str(e))

def test_chat_auth():
    try:
        headers = {"X-API-Key": API_KEY}
        r = requests.post(f"{BASE_URL}/chat", json={"question": "Who is the candidate?", "sessionId": "test-session"}, headers=headers)
        if r.status_code == 200:
            print(f"   Chat Response: {r.json().get('response')[:50]}...")
            print_result("Chat Auth", True)
        else:
            print_result("Chat Auth", False, f"Status {r.status_code} - {r.text}")
    except Exception as e:
        print_result("Chat Auth", False, str(e))

def test_wipe_auth():
    try:
        headers = {"X-API-Key": API_KEY}
        r = requests.post(f"{BASE_URL}/wipe", json={"sessionId": "test-session"}, headers=headers)
        if r.status_code == 200:
            print_result("Wipe Auth", True)
        else:
            print_result("Wipe Auth", False, f"Status {r.status_code} - {r.text}")
    except Exception as e:
        print_result("Wipe Auth", False, str(e))

def test_logic_flow():
    session_id = "logic-test-session"
    headers = {"X-API-Key": API_KEY}
    
    print("\n[TEST] Starting Business Logic Flow Verification...")
    
    # 1. Clean start
    requests.post(f"{BASE_URL}/wipe", json={"sessionId": session_id}, headers=headers)
    
    # 2. Verify Empty
    r = requests.get(f"{BASE_URL}/status", params={"sessionId": session_id}, headers=headers)
    if r.json().get("isEmpty") is True:
        print_result("Pre-Ingest Status (Empty)", True)
    else:
        print_result("Pre-Ingest Status (Empty)", False, "DB not empty initially")
        return

    # 3. Ingest
    payload = {
        "text": "CANDIDATE: Alice Wonderland\nEmail: alice@example.com\nSkill: Advanced AI Logic.",
        "sessionId": session_id
    }
    r = requests.post(f"{BASE_URL}/ingest/text", json=payload, headers=headers)
    if r.status_code == 200:
        print_result("Ingestion", True)
    else:
        print_result("Ingestion", False, r.text)
        return

    # 4. Verify Not Empty
    r = requests.get(f"{BASE_URL}/status", params={"sessionId": session_id}, headers=headers)
    if r.json().get("isEmpty") is False:
        print_result("Post-Ingest Status (Not Empty)", True)
    else:
        print_result("Post-Ingest Status (Not Empty)", False, "DB reported empty after ingest")
        return

    # 5. Chat Verify
    chat_payload = {"question": "What is Alice's skill?", "sessionId": session_id}
    r = requests.post(f"{BASE_URL}/chat", json=chat_payload, headers=headers)
    response_text = r.json().get("response", "").lower()
    if "ai logic" in response_text or "advanced" in response_text:
        print_result("Chat Logic (Answer Correct)", True)
    else:
        print_result("Chat Logic (Answer Correct)", False, f"Response: {response_text}")

    # 6. Wipe
    requests.post(f"{BASE_URL}/wipe", json={"sessionId": session_id}, headers=headers)
    
    # 7. Verify Empty Again
    r = requests.get(f"{BASE_URL}/status", params={"sessionId": session_id}, headers=headers)
    if r.json().get("isEmpty") is True:
        print_result("Post-Wipe Status (Empty)", True)
    else:
        print_result("Post-Wipe Status (Empty)", False, "DB not empty after wipe")

if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: APP_API_KEY not found in .env")
        sys.exit(1)
        
    print(f"Testing API at {BASE_URL} with Key: {API_KEY[:4]}***")
    # Run simple checks
    test_health()
    test_ingest_no_auth()
    
    # Run full logic flow
    test_logic_flow()
