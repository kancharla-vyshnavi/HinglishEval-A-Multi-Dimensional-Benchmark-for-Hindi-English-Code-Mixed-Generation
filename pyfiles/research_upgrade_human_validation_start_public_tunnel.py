"""
start_public_tunnel.py
Launches Cloudflare Tunnel for public HTTPS access to the HinglishEval platform.
Extracts the trycloudflare.com URL, tests it live, updates ACTIVE_LINKS files,
and keeps the tunnel connection active indefinitely.
"""

import os
import sys
import re
import time
import json
import urllib.request
import subprocess
import threading

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED_BIN = os.path.join(BASE_DIR, "bin", "cloudflared.exe")
LINKS_JSON = os.path.join(BASE_DIR, "ACTIVE_LINKS.json")
LINKS_TXT = os.path.join(BASE_DIR, "ACTIVE_LINKS.txt")
TUNNEL_URL_FILE = os.path.join(BASE_DIR, "TUNNEL_URL.txt")

TOKEN_A = "eval_a_lead_2026"

def verify_url(url: str, timeout: int = 15) -> bool:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception as e:
        return False

def main():
    if not os.path.exists(CLOUDFLARED_BIN):
        print(f"Error: cloudflared not found at {CLOUDFLARED_BIN}")
        sys.exit(1)

    port = 8000
    cmd = [CLOUDFLARED_BIN, "tunnel", "--url", f"http://127.0.0.1:{port}"]
    print(f"Starting tunnel: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    tunnel_url = None
    start_time = time.time()

    # Read stderr for the trycloudflare URL
    for line in proc.stderr:
        line_clean = line.strip()
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line_clean)
        if match:
            tunnel_url = match.group(0)
            print(f"[FOUND] Cloudflare Tunnel URL: {tunnel_url}")
            break
        if time.time() - start_time > 30:
            print("Timeout waiting for Cloudflare tunnel URL.")
            break

    if not tunnel_url:
        print("Failed to capture public tunnel URL.")
        proc.terminate()
        sys.exit(1)

    # Save to TUNNEL_URL.txt
    with open(TUNNEL_URL_FILE, "w", encoding="utf-8") as f:
        f.write(tunnel_url + "\n")

    public_a_url = f"{tunnel_url}/?token={TOKEN_A}&item=430"
    public_a_default = f"{tunnel_url}/?token={TOKEN_A}"

    print(f"\n[TESTING] Verifying public reachability: {public_a_url} ...")
    reachable = False
    for attempt in range(10):
        time.sleep(1)
        if verify_url(f"{tunnel_url}/api/session?token={TOKEN_A}", timeout=5):
            reachable = True
            break
        print(f"  Attempt {attempt+1}/10...")

    if reachable:
        print("[SUCCESS] Public HTTPS tunnel is LIVE and responding 200 OK!")
    else:
        print("[WARN] Tunnel launched, DNS propagating...")

    # Update ACTIVE_LINKS.json
    active_data = {
        "status": "annotator_a_only",
        "active_mode": "Single Annotator (Lead)",
        "public_url_annotator_a": public_a_url,
        "public_tunnel_base": tunnel_url,
        "local_annotator_a": f"http://127.0.0.1:{port}/?token={TOKEN_A}&item=430",
        "annotator_b_access": "disabled",
        "token_a": TOKEN_A,
        "token_b": "DISABLED",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(LINKS_JSON, "w", encoding="utf-8") as f:
        json.dump(active_data, f, indent=2)

    # Update ACTIVE_LINKS.txt
    txt_content = f"""================================================================================
HINGLISHEVAL ACTIVE EVALUATION LINKS (PUBLIC HTTPS ACTIVE)
================================================================================

1. Annotator A (You - Lead Researcher) - PUBLIC LINK:
   Direct Resume Link:   {public_a_url}
   Default Public Link:  {public_a_default}
   Local Host Link:      http://127.0.0.1:{port}/?token={TOKEN_A}&item=430
   Access Token:         {TOKEN_A}
   Status:               ACTIVE (429 completed, 71 remaining, starting at item #430)

2. Annotator B (Partner Evaluator):
   Status:               DISABLED (Partner access revoked)

================================================================================
"""
    with open(LINKS_TXT, "w", encoding="utf-8") as f:
        f.write(txt_content)

    print("\n" + "=" * 80)
    print(f"PUBLIC LINK READY:")
    print(f"{public_a_url}")
    print("=" * 80 + "\n")

    # Keep tunnel alive
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    main()
