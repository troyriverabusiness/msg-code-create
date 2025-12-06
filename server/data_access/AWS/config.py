import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET = os.getenv("AWS_SECRET")
AWS_SHORT_TERM_KEY = os.getenv("AWS_SHORT_TERM_KEY")
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Provide clear, accurate, and concise responses."
)
