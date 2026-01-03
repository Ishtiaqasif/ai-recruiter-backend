import requests
import os
import sys
import uuid
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("APP_API_KEY")

if not API_KEY:
    print("ERROR: APP_API_KEY not found in .env. Cannot authenticate.")
    sys.exit(1)

HEADERS = {"X-API-Key": API_KEY}

def run_test():
    session_id = f"wipe-test-{uuid.uuid4().hex[:6]}"
    print(f"\n[TEST] Verifying Wipe for Session: {session_id}")
    
    # 1. Check Empty Initially
    print("1. Checking initial status...")
    r = requests.get(f"{BASE_URL}/status", params={"sessionId": session_id}, headers=HEADERS)
    if not r.json().get("isEmpty"):
        print("[FAIL] Session not initially empty!")
        return
    print("   [OK] Session is empty.")

    # 2. Ingest Data
    print("2. Ingesting test document...")
    # Must include an email for ingestion to work
    resume_text = f"CANDIDATE: Metric Tester\nEMAIL: test_{uuid.uuid4().hex[:6]}@example.com\n\nThis is ephemeral data for session {session_id}."
    payload = {
        "text": resume_text,
        "sessionId": session_id
    }
    r = requests.post(f"{BASE_URL}/ingest/text", json=payload, headers=HEADERS)
    if r.status_code != 200:
        print(f"[FAIL] Ingest failed: {r.text}")
        return
    print("   [OK] Ingest request successful.")

    # Wait a moment for persistence (mostly instant for Mongo)
    time.sleep(1)

    # 3. Verify Not Empty
    print("3. Verifying persistence...")
    r = requests.get(f"{BASE_URL}/status", params={"sessionId": session_id}, headers=HEADERS)
    if r.json().get("isEmpty"):
        print("[FAIL] Session reported empty after ingest! (Ingestion/Persistence failure)")
        return
    print("   [OK] Session contains data.")

    # 4. Perform Wipe
    print("4. Executing wipe...")
    payload = {"sessionId": session_id}
    r = requests.post(f"{BASE_URL}/wipe", json=payload, headers=HEADERS)
    if r.status_code != 200:
        print(f"[FAIL] Wipe request failed: {r.text}")
        return
    print(f"   [OK] Wipe response: {r.json()}")

    # 5. Verify Empty Again
    print("5. Verifying cleanup...")
    r = requests.get(f"{BASE_URL}/status", params={"sessionId": session_id}, headers=HEADERS)
    if not r.json().get("isEmpty"):
        print("[FAIL] Session NOT empty after wipe! (Deletion failure)")
        return
    print("   [OK] Session is empty.")
    
    with open("wipe_results.txt", "w") as f:
        f.write(f"Session: {session_id}\n")
        f.write("Status: SUCCESS\n")
        f.write("Steps Verified: Initial Empty -> Ingest -> Persistence -> Wipe -> Final Empty\n")
        
    print("\n[SUCCESS] Wipe logic verified correctly.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"\n[ERROR] Test crashed: {e}")
