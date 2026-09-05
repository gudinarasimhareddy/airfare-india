import uvicorn
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    print(">> Starting AirfareX India Full-Stack Server...")
    print(">> Web Application: http://127.0.0.1:8000")
    print(">> OpenAPI / Swagger Docs: http://127.0.0.1:8000/docs")
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=False)
