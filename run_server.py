import uvicorn
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"

    print(">> Starting AirfareX India Full-Stack Server for ALL DEVICES...")
    print(f">> Local Host:       http://127.0.0.1:8000")
    print(f">> Network / Devices: http://{local_ip}:8000")
    print(f">> Wi-Fi Direct:     http://10.221.83.242:8000")
    print(f">> OpenAPI Docs:     http://127.0.0.1:8000/docs")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)
