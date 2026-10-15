"""
Cloudflare Tunnel Launcher for HinglishEval Human Validation Web Platform.
Spawns local cloudflared daemon, captures trycloudflare.com HTTPS URL,
tests /health endpoint live, and writes active links.
"""

import os
import sys
import re
import time
import json
import urllib.request
import subprocess
from pathlib import Path

# UTF-8 stdout configuration for Windows
sys.stdout.reconfigure(encoding="utf-8")

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
CLOUDFLARED_BIN = PROJECT_ROOT / "research_upgrade" / "human_validation" / "bin" / "cloudflared.exe"

TUNNEL_URL_FILE = APP_DIR / "TUNNEL_URL.txt"
ACTIVE_LINKS_JSON = APP_DIR / "ACTIVE_LINKS.json"
ACTIVE_LINKS_TXT = APP_DIR / "ACTIVE_LINKS.txt"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from human_validation_app.config import ANNOTATOR_A_KEY, ANNOTATOR_B_KEY, ADMIN_SECRET


def verify_url(url: str, timeout: int = 15) -> bool:
    """Verify live HTTP 200 on /health endpoint."""
    try:
        req = urllib.request.Request(
            f"{url}/health",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    if not CLOUDFLARED_BIN.exists():
        print(f"Error: cloudflared binary not found at {CLOUDFLARED_BIN}")
        sys.exit(1)

    port = int(os.getenv("PORT", "8000"))
    cmd = [str(CLOUDFLARED_BIN), "tunnel", "--url", f"http://127.0.0.1:{port}"]
    print(f"Starting tunnel on http://127.0.0.1:{port}...")

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
        print(line, end="")
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            tunnel_url = match.group(0)
            break
        if time.time() - start_time > 45:
            print("Timeout waiting for Cloudflare tunnel URL.")
            break

    if not tunnel_url:
        print("Failed to acquire Cloudflare tunnel URL.")
        proc.kill()
        sys.exit(1)

    print(f"\nDiscovered Tunnel URL: {tunnel_url}")
    print("Testing live HTTPS reachability...")

    verified = False
    for attempt in range(1, 15):
        time.sleep(2)
        if verify_url(tunnel_url):
            verified = True
            print(f"Verified live HTTPS reachability on attempt {attempt}!")
            break
        print(f"Attempt {attempt}: Waiting for tunnel routing...")

    if not verified:
        print("Warning: Live verification timed out. Tunnel might still be establishing routes.")

    # Save URLs
    with open(TUNNEL_URL_FILE, "w", encoding="utf-8") as f:
        f.write(tunnel_url + "\n")

    links = {
        "tunnel_url": tunnel_url,
        "annotator_a_link": f"{tunnel_url}/?token={ANNOTATOR_A_KEY}",
        "annotator_b_link": f"{tunnel_url}/?token={ANNOTATOR_B_KEY}",
        "admin_export_link": f"{tunnel_url}/api/admin/export?admin_key={ADMIN_SECRET}",
        "health_check_link": f"{tunnel_url}/health",
        "verified": verified,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

    with open(ACTIVE_LINKS_JSON, "w", encoding="utf-8") as f:
        json.dump(links, f, indent=2)

    with open(ACTIVE_LINKS_TXT, "w", encoding="utf-8") as f:
        f.write(f"=== HinglishEval Live Links ===\n")
        f.write(f"Website URL:      {tunnel_url}\n")
        f.write(f"Annotator A:      {links['annotator_a_link']}\n")
        f.write(f"Annotator B:      {links['annotator_b_link']}\n")
        f.write(f"Health Endpoint:  {links['health_check_link']}\n")
        f.write(f"Admin Export:     {links['admin_export_link']}\n")

    print(f"Active links saved to {ACTIVE_LINKS_TXT}")

    # Drain stderr in background thread to prevent pipe buffering issues
    import threading
    def drain_pipe():
        try:
            for l in proc.stderr:
                pass
        except Exception:
            pass

    t = threading.Thread(target=drain_pipe, daemon=True)
    t.start()

    # Keep process active
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    main()
