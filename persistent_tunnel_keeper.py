"""
AirfareX India — Persistent Tunnel Watchdog
Ensures the global HTTPS tunnel stays active 24/7 with automatic HTTP2 reconnects.
"""
import subprocess
import time
import re
import os
import sys

CLOUDFLARED_EXE = r"C:\Users\dgowt\.gemini\antigravity-ide\scratch\cloudflared.exe"
LINK_FILE = r"c:\Users\dgowt\OneDrive\Desktop\airfare india\ACTIVE_GLOBAL_URL.txt"

def run_tunnel():
    print(">> Starting Cloudflare HTTP2 Global Tunnel...")
    cmd = [CLOUDFLARED_EXE, "tunnel", "--url", "http://127.0.0.1:8000", "--protocol", "http2"]
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="ignore"
    )
    
    tunnel_url = None
    for line in iter(proc.stdout.readline, ''):
        if not line:
            break
        print(line.strip())
        
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            tunnel_url = match.group(0)
            print("\n" + "=" * 60)
            print(f">> ACTIVE GLOBAL LINK: {tunnel_url}")
            print("=" * 60 + "\n")
            with open(LINK_FILE, "w", encoding="utf-8") as f:
                f.write(f"AirfareX India — Active Global Link:\n{tunnel_url}\n\nBooking Page:\n{tunnel_url}/booking.html\n")
    
    proc.wait()
    print(">> Tunnel process disconnected. Reconnecting in 5 seconds...")
    time.sleep(5)

if __name__ == "__main__":
    while True:
        try:
            run_tunnel()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Watchdog error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
