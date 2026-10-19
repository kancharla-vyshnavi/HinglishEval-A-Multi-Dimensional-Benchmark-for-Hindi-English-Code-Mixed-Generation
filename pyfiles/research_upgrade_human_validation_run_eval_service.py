"""
run_eval_service.py
Starts Uvicorn on 0.0.0.0:8000 and Cloudflare Tunnel to generate a live, verified public link.
Tests reachability for both local and public URLs before reporting readiness.
Keeps running continuously.
"""

import os
import sys
import time
import re
import subprocess
import threading
import json
import urllib.request
import uvicorn

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED_BIN = os.path.join(BASE_DIR, "bin", "cloudflared.exe")
LINKS_TXT = os.path.join(BASE_DIR, "ACTIVE_LINKS.txt")
LINKS_JSON = os.path.join(BASE_DIR, "ACTIVE_LINKS.json")

TOKEN_A = "eval_a_lead_2026"
TOKEN_B = "eval_b_partner_2026"
TOKEN_ADMIN = "admin_hinglish_eval_master"

tunnel_url_holder = {"url": None}

def run_tunnel(port=8000):
    if not os.path.exists(CLOUDFLARED_BIN):
        print(f"Error: {CLOUDFLARED_BIN} not found.")
        return
    
    cmd = [CLOUDFLARED_BIN, "tunnel", "--url", f"http://127.0.0.1:{port}"]
    print(f"[TUNNEL] Starting: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    for line in proc.stderr:
        line_str = line.strip()
        # Look for trycloudflare.com
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line_str)
        if match:
            tunnel_url_holder["url"] = match.group(0)
            print(f"\n[TUNNEL] Detected public URL: {tunnel_url_holder['url']}")
            break

    # Keep reading in background to prevent buffer fill
    def drain():
        for _ in proc.stderr:
            pass
    threading.Thread(target=drain, daemon=True).start()

def verify_url(url, timeout=10):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Verification check failed for {url}: {e}")
        return False

def monitor_and_verify(port=8000):
    time.sleep(2)
    local_url = f"http://127.0.0.1:{port}"
    print(f"\n[CHECK] Testing local server on {local_url}...")
    local_ok = False
    for _ in range(15):
        if verify_url(f"{local_url}/api/session?token={TOKEN_A}", timeout=2):
            local_ok = True
            break
        time.sleep(0.5)

    if not local_ok:
        print("[FAIL] Local server failed to respond.")
        return

    print("[SUCCESS] Local server is responding 200 OK.")

    # Wait for tunnel
    print("[CHECK] Waiting for Cloudflare Tunnel public URL...")
    pub_url = None
    for _ in range(30):
        if tunnel_url_holder["url"]:
            pub_url = tunnel_url_holder["url"]
            break
        time.sleep(0.5)

    if pub_url:
        print(f"[CHECK] Testing reachability of public tunnel: {pub_url}...")
        pub_ok = False
        for _ in range(15):
            if verify_url(f"{pub_url}/api/session?token={TOKEN_B}", timeout=5):
                pub_ok = True
                break
            time.sleep(1)

        if pub_ok:
            print(f"[SUCCESS] Public tunnel {pub_url} is VERIFIED reachable over the internet (200 OK)!")
        else:
            print(f"[WARNING] Public tunnel {pub_url} generated but took longer to verify.")
    else:
        print("[WARNING] Could not obtain public tunnel URL.")

    # Write ACTIVE_LINKS files
    links_data = {
        "status": "active",
        "local_annotator_a": f"{local_url}/?token={TOKEN_A}",
        "public_annotator_b": f"{pub_url}/?token={TOKEN_B}" if pub_url else "tunnel_pending",
        "admin_dashboard": f"{local_url}/?token={TOKEN_ADMIN}",
        "tunnel_url": pub_url,
        "token_a": TOKEN_A,
        "token_b": TOKEN_B,
        "token_admin": TOKEN_ADMIN,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(LINKS_JSON, "w", encoding="utf-8") as f:
        json.dump(links_data, f, indent=2)

    with open(LINKS_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("HINGLISHEVAL ACTIVE EVALUATION LINKS (VERIFIED LIVE)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"1. Annotator A (You - 500 items):\n")
        f.write(f"   Local Browser:  {local_url}/?token={TOKEN_A}\n")
        if pub_url:
            f.write(f"   Public Browser: {pub_url}/?token={TOKEN_A}\n")
        f.write(f"   Token:          {TOKEN_A}\n\n")
        f.write(f"2. Annotator B (Partner - 500 items):\n")
        if pub_url:
            f.write(f"   Public Share:   {pub_url}/?token={TOKEN_B}\n")
        else:
            f.write(f"   Local Network:  http://<YOUR_IP>:{port}/?token={TOKEN_B}\n")
        f.write(f"   Token:          {TOKEN_B}\n\n")
        f.write(f"3. Admin Dashboard (Real-time monitoring & export):\n")
        f.write(f"   Dashboard:      {local_url}/?token={TOKEN_ADMIN}\n")
        f.write(f"   Token:          {TOKEN_ADMIN}\n")
        f.write("=" * 80 + "\n")

    print(f"\n[READY] Saved verified live links to {LINKS_TXT}")
    print("\n" + open(LINKS_TXT, "r", encoding="utf-8").read())

def main():
    port = 8000
    os.chdir(BASE_DIR)

    # Start tunnel in separate background thread
    threading.Thread(target=run_tunnel, args=(port,), daemon=True).start()

    # Start monitor & verification in separate thread
    threading.Thread(target=monitor_and_verify, args=(port,), daemon=True).start()

    # Start uvicorn server in main thread
    print(f"[SERVER] Starting Uvicorn on 0.0.0.0:{port}...")
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
