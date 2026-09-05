"""
AirfareX India — Push to GitHub Repository
Project: https://github.com/gudinarasimhareddy/airfare-india.git
"""
import sys
import os
import dulwich.porcelain as porcelain

def push_repo(token=None):
    if not token:
        token = os.environ.get("GITHUB_TOKEN")
    
    if not token and len(sys.argv) > 1:
        token = sys.argv[1].strip()

    if not token:
        print("Usage: python push_to_github.py <YOUR_GITHUB_PERSONAL_ACCESS_TOKEN>")
        print("Or set GITHUB_TOKEN environment variable.")
        return False

    remote_url = f"https://{token}@github.com/gudinarasimhareddy/airfare-india.git"
    print(f"Pushing active 'main' branch to https://github.com/gudinarasimhareddy/airfare-india.git...")

    try:
        porcelain.push('.', remote_url, 'refs/heads/main:refs/heads/main')
        print("\n🎉 SUCCESS! All files, commits, and branches pushed to GitHub!")
        print("Repository: https://github.com/gudinarasimhareddy/airfare-india")
        return True
    except Exception as err:
        print(f"\n❌ Push failed: {err}")
        print("Please verify your GitHub token has 'repo' or 'contents:write' scope permissions.")
        return False

if __name__ == "__main__":
    push_repo()
