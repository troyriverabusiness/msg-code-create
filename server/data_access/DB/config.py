import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"
CLIENT_ID = os.getenv("TROY_API_CLIENT")
API_KEY = os.getenv("TROY_API_KEY")
DATA_DIR = Path(__file__).parent.parent.parent / "api_data"


def get_headers() -> dict:
    if not CLIENT_ID or not API_KEY:
        raise ValueError(
            "Missing API credentials. Ensure TROY_API_CLIENT and TROY_API_KEY are set in .env"
        )

    return {
        "DB-Client-Id": CLIENT_ID,
        "DB-Api-Key": API_KEY,
        "Accept": "application/xml",
    }


def save_response(filename: str, content: str) -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    filepath = DATA_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath


def print_separator(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
