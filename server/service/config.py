"""
Shared configuration for DB Timetables API services.

Loads credentials from .env file and provides common utilities.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from server directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# API Configuration
BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"

# Credentials - using TROY credentials by default, can be switched to LARS
CLIENT_ID = os.getenv("TROY_CLIENT_ID")
API_KEY = os.getenv("TROY_API_KEY")

# Alternative: Use LARS credentials
# CLIENT_ID = os.getenv("LARS_CLIENT_ID")
# API_KEY = os.getenv("LARS_API_KEY")

# AWS Bedrock Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET = os.getenv("AWS_SECRET")
AWS_REGION = "eu-central-1"
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# Data directory for saving responses
DATA_DIR = Path(__file__).parent.parent / "data"


def get_headers() -> dict:
    """
    Get the authentication headers for API requests.

    Returns:
        dict: Headers with DB-Client-Id and DB-Api-Key
    """
    if not CLIENT_ID or not API_KEY:
        raise ValueError(
            "Missing API credentials. Please ensure TROY_CLIENT_ID and TROY_API_KEY "
            "are set in the .env file."
        )

    return {
        "DB-Client-Id": CLIENT_ID,
        "DB-Api-Key": API_KEY,
        "Accept": "application/xml",
    }


def save_response(filename: str, content: str) -> Path:
    """
    Save API response content to a file in the data directory.

    Args:
        filename: Name of the file (without path)
        content: Content to save

    Returns:
        Path: Full path to the saved file
    """
    DATA_DIR.mkdir(exist_ok=True)
    filepath = DATA_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath


def print_separator(title: str):
    """Print a visual separator with a title."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
