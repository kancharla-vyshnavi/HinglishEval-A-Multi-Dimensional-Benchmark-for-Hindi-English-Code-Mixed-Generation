"""
launch_evaluation_server.py
Launches the HinglishEval human evaluation web platform.
Features:
- Starts Uvicorn server on host 0.0.0.0:8000
- Optionally launches Cloudflare Tunnel (cloudflared.exe) to generate a public HTTPS link
- Displays dedicated, secure tokens and URLs for Annotator A, Annotator B, and Admin
"""

import os
import sys
import time
import re
import subprocess
import argparse
from typing import Optional, Tuple
import uvicorn

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED_BIN = os.path.join(BASE_DIR, "bin", "cloudflared.exe")

TOKEN_A = "eval_a_lead_2026"
TOKEN_B = "eval_b_partner_2026"
TOKEN_ADMIN = "admin_hinglish_eval_master"

def start_tunnel(port: int = 8000) -> Tuple[Optional[subprocess.Popen], Optional[str]]:
    if not os.path.exists(CLOUDFLARED_BIN):
        print(f"Note: Cloudflare Tunnel binary not found at {CLOUDFLARED_BIN}.")
        return None, None
    
    cmd = [CLOUDFLARED_BIN, "tunnel", "--url", f"http://127.0.0.1:{port}"]
    print(f"Launching Cloudflare Tunnel: {' '.join(cmd)}")
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    tunnel_url = None
    start_t = time.time()
    # Read stderr to extract the trycloudflare.com URL
    while time.time() - start_t < 15:
        line = proc.stderr.readline()
        if not line:
            time.sleep(0.1)
            continue
        # Look for trycloudflare.com
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if match:
            tunnel_url = match.group(0)
            break

    return proc, tunnel_url

def main():
    parser = argparse.ArgumentParser(description="HinglishEval Human Evaluation Server Launcher")
    parser.add_argument("--port", type=int, default=8000, help="Port to run web server on")
    parser.add_argument("--tunnel", action="store_true", help="Launch Cloudflare tunnel for public internet sharing")
    parser.add_argument("--no-server", action="store_true", help="Do not start uvicorn (for tunnel testing)")

    args = parser.parse_args()

    port = args.port
    tunnel_proc = None
    public_url = None

    if args.tunnel:
        tunnel_proc, public_url = start_tunnel(port)

    print("\n" + "=" * 80)
    print("HINGLISHEVAL HUMAN EVALUATION PLATFORM READY")
    print("=" * 80)
    print(f"\n[Local Host]: http://127.0.0.1:{port}")
    if public_url:
        print(f"[Public HTTPS Tunnel]: {public_url}")
    else:
        print("[Public Tunnel]: Not active (use --tunnel to enable or share via LAN/export)")

    print("\n" + "-" * 80)
    print("DEDICATED ACCESS URLS & TOKENS (SINGLE ANNOTATOR MODE):")
    print("-" * 80)
    print(f"Annotator A (Lead Researcher - Active):")
    print(f"  Local Active URL: http://127.0.0.1:{port}/?token={TOKEN_A}")
    print(f"  Resume URL (71 remaining): http://127.0.0.1:{port}/?token={TOKEN_A}&item=430")
    print(f"  Token:            {TOKEN_A}")
    print(f"  Progress:         429 completed / 71 pending (items 430-500)")
    print(f"\nAnnotator B (Partner Evaluator):")
    print(f"  Access:           DISABLED (Partner access revoked; 15 completed ratings safely backed up)")
    print(f"\nProject Lead / Admin (Live Monitoring & Combined Export):")
    print(f"  Dashboard URL:    http://127.0.0.1:{port}/?token={TOKEN_ADMIN}")
    print(f"  Token:            {TOKEN_ADMIN}")
    print("=" * 80 + "\n")

    if not args.no_server:
        os.chdir(BASE_DIR)
        try:
            uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")
        finally:
            if tunnel_proc:
                tunnel_proc.terminate()

if __name__ == "__main__":
    main()
