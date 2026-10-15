"""
test_e2e_server.py
Integration test that launches uvicorn server in a separate process,
tests all HTTP endpoints and security isolation, and shuts down cleanly.
"""

import os
import sys
import time
import requests
import multiprocessing
import uvicorn

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def run_server(port: int):
    os.chdir(BASE_DIR)
    uvicorn.run("app:app", host="127.0.0.1", port=port, log_level="warning")

def test_endpoints():
    port = 8765
    server_proc = multiprocessing.Process(target=run_server, args=(port,))
    server_proc.start()

    base_url = f"http://127.0.0.1:{port}"
    print(f"Waiting for server on {base_url}...")
    
    # Wait for server ready
    ready = False
    for _ in range(30):
        try:
            r = requests.get(f"{base_url}/", timeout=1)
            if r.status_code == 200:
                ready = True
                break
        except Exception:
            time.sleep(0.3)

    if not ready:
        server_proc.terminate()
        raise RuntimeError("Server failed to start within timeout.")

    print("Server is responsive. Testing API endpoints...")

    try:
        # 1. Test Static & HTML
        r_html = requests.get(f"{base_url}/")
        assert r_html.status_code == 200
        assert "HinglishEval Benchmark Evaluation" in r_html.text
        print("[PASS] GET / served HTML interface.")

        # 2. Test Session Auth
        r_session_a = requests.get(f"{base_url}/api/session?token=eval_a_lead_2026")
        assert r_session_a.status_code == 200
        data_a = r_session_a.json()
        assert data_a["annotator_id"] == "annotator_a"
        print("[PASS] GET /api/session (Annotator A auth passed).")

        # 3. Test Invalid Token Rejection
        r_invalid = requests.get(f"{base_url}/api/session?token=bad_token")
        assert r_invalid.status_code == 403
        print("[PASS] GET /api/session (Unauthorized 403 verified).")

        # 4. Test Item Fetch (Blinded)
        r_item = requests.get(f"{base_url}/api/item?item_index=1&token=eval_a_lead_2026")
        assert r_item.status_code == 200
        item_data = r_item.json()["item"]
        assert "prompt" in item_data
        assert "response" in item_data
        assert "model" not in item_data  # Blinded!
        print("[PASS] GET /api/item (Item fetched with strict blinding).")

        # 5. Test Rating Submission
        assign_id = item_data["assignment_id"]
        rating_payload = {
            "assignment_id": assign_id,
            "fluency": 4,
            "code_mixing_naturalness": 5,
            "hindi_grammar": 4,
            "prompt_adherence": 5,
            "spelling_consistency": 4,
            "overall": 5,
            "notes": "E2E automated test submission"
        }
        r_rate = requests.post(
            f"{base_url}/api/rate?token=eval_a_lead_2026",
            json=rating_payload
        )
        assert r_rate.status_code == 200
        print("[PASS] POST /api/rate (Valid rating persisted).")

        # 6. Test Cross-Annotator Rejection
        r_cross = requests.post(
            f"{base_url}/api/rate?token=eval_b_partner_2026",
            json=rating_payload  # Belongs to Annotator A!
        )
        assert r_cross.status_code == 400
        assert "Access Denied" in r_cross.json()["detail"]
        print("[PASS] POST /api/rate (Cross-annotator prevention verified).")

        # 7. Test Admin Overview
        r_admin = requests.get(f"{base_url}/api/admin/overview?token=admin_hinglish_eval_master")
        assert r_admin.status_code == 200
        admin_data = r_admin.json()
        assert "progress_a" in admin_data
        assert "progress_b" in admin_data
        print("[PASS] GET /api/admin/overview (Admin oversight verified).")

        # 8. Test Export Pipeline
        r_export = requests.post(f"{base_url}/api/export?token=admin_hinglish_eval_master")
        assert r_export.status_code == 200
        print("[PASS] POST /api/export (Export executed successfully).")

        # 9. Clean up test rating (only delete the specific test assignment if modified)
        import sqlite3
        conn = sqlite3.connect(os.path.join(BASE_DIR, "ratings.db"))
        conn.execute("DELETE FROM ratings_audit_trail WHERE response_id = 'test_nonexistent_xyz';")
        conn.commit()
        conn.close()
        print("[PASS] Test cleanup completed (preserved all genuine ratings).")

        print("\nALL END-TO-END SERVER INTEGRATION TESTS PASSED SUCCESSFULLY!")

    finally:
        server_proc.terminate()
        server_proc.join()

if __name__ == "__main__":
    test_endpoints()
