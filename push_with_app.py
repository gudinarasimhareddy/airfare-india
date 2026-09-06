"""
Push to GitHub repository using GitHub App private key.
Project: https://github.com/gudinarasimhareddy/airfare-india.git
"""
import sys
import os
import time
import base64
import json
import urllib.request
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import dulwich.porcelain as porcelain

def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii')

def create_jwt(app_id: int, private_key_path: str) -> str:
    with open(private_key_path, 'rb') as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    
    now = int(time.time())
    header = b64url(json.dumps({'alg': 'RS256', 'typ': 'JWT'}).encode())
    payload = b64url(json.dumps({
        'iat': now - 60,
        'exp': now + 600,
        'iss': app_id
    }).encode())
    
    signing_input = f"{header}.{payload}".encode('ascii')
    sig = key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    return f"{header}.{payload}.{b64url(sig)}"

def get_installation_token(app_id: int, private_key_path: str, repo_owner: str, repo_name: str) -> str:
    jwt = create_jwt(app_id, private_key_path)
    
    # 1. Find installation for repo
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/installation",
        headers={
            "Authorization": f"Bearer {jwt}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "AirfareX-Uploader"
        }
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            installation_id = data["id"]
            print(f"Found GitHub App installation ID: {installation_id}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 404:
            raise RuntimeError(
                "GitHub App is not installed on this repository yet!\n"
                "Please go to your GitHub App settings -> 'Install App' in the left sidebar, and install it to your account or repository."
            )
        raise RuntimeError(f"Failed to find installation (HTTP {e.code}): {body}")

    # 2. Create installation access token
    req2 = urllib.request.Request(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        data=b"{}",
        headers={
            "Authorization": f"Bearer {jwt}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "AirfareX-Uploader"
        },
        method="POST"
    )
    
    with urllib.request.urlopen(req2) as resp2:
        token_data = json.loads(resp2.read().decode())
        return token_data["token"]

def push(app_id: int, pem_path: str):
    repo_owner = "gudinarasimhareddy"
    repo_name = "airfare-india"
    
    print(f"Authenticating GitHub App (App ID: {app_id})...")
    token = get_installation_token(app_id, pem_path, repo_owner, repo_name)
    print("Obtained installation access token.")
    
    remote_url = f"https://x-access-token:{token}@github.com/{repo_owner}/{repo_name}.git"
    print(f"Pushing active branch to https://github.com/{repo_owner}/{repo_name}.git...")
    porcelain.push('.', remote_url, 'refs/heads/main:refs/heads/main')
    print("\nSUCCESS! All code, commits, and files pushed to GitHub successfully!")
    print(f"Repository: https://github.com/{repo_owner}/{repo_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python push_with_app.py <APP_ID>")
        sys.exit(1)
    
    app_id = int(sys.argv[1].strip())
    pem_path = r"c:\Users\dgowt\Downloads\air-fare-india.2026-09-05.private-key.pem"
    push(app_id, pem_path)
