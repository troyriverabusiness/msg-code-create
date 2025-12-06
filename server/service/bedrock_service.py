"""
AWS Bedrock integration service for Claude AI conversations.
"""

import boto3
import requests
from typing import List, Dict, Optional
from botocore.exceptions import ClientError, BotoCoreError


# TODO: Update system prompt to customize AI behavior for your specific use case
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Provide clear, accurate, and concise responses."
)


class BedrockService:
    """Service for interacting with AWS Bedrock Runtime API."""

    def __init__(
        self, aws_access_key: str, aws_secret_key: str, region: str = "eu-central-1"
    ):
        """
        Initialize Bedrock service.

        Args:
            aws_access_key: AWS access key for authentication
            aws_secret_key: AWS secret key for authentication
            region: AWS region (default: eu-central-1)
        """
        self.region = region
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

        # Initialize boto3 Bedrock Runtime client
        try:
            self.client = boto3.client(
                service_name="bedrock-runtime",
                region_name=region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Bedrock client: {str(e)}")

    def send_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> str:
        """
        Send a message to Claude via Bedrock and get response.

        Args:
            message: User's message
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
            system_prompt: System prompt to guide AI behavior

        Returns:
            AI assistant's response text

        Raises:
            RuntimeError: If API call fails
        """
        # Build messages array for Bedrock Converse API
        messages = []

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append(
                    {"role": msg["role"], "content": [{"text": msg["content"]}]}
                )

        # Add current user message
        messages.append({"role": "user", "content": [{"text": message}]})

        try:
            # Call Bedrock Converse API
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "maxTokens": 2048,
                    "temperature": 0.7,
                },
            )

            # Extract response text
            output_message = response["output"]["message"]
            assistant_text = output_message["content"][0]["text"]

            return assistant_text

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))
            raise RuntimeError(f"Bedrock API error ({error_code}): {error_message}")

        except BotoCoreError as e:
            raise RuntimeError(f"AWS connection error: {str(e)}")

        except KeyError as e:
            raise RuntimeError(f"Unexpected API response format: {str(e)}")

        except Exception as e:
            raise RuntimeError(f"Unexpected error calling Bedrock: {str(e)}")

    def send_message_http(
        self,
        bearer_token: str,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        model_id: Optional[str] = None,
    ) -> str:
        """
        Send a message to Claude via direct HTTP request using Bearer token.

        Args:
            bearer_token: Short-term AWS Bedrock API token from .env
            message: User's message
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
            system_prompt: System prompt to guide AI behavior
            model_id: Optional model ID override (default: uses self.model_id)

        Returns:
            AI assistant's response text

        Raises:
            RuntimeError: If HTTP request fails
        """
        # Use provided model_id or default
        target_model = model_id or self.model_id

        # Build messages array
        messages = []

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append(
                    {"role": msg["role"], "content": [{"text": msg["content"]}]}
                )

        # Add current user message
        messages.append({"role": "user", "content": [{"text": message}]})

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        }

        # Prepare payload
        payload = {
            "messages": messages,
            "system": [{"text": system_prompt}],
            "inferenceConfig": {
                "maxTokens": 2048,
                "temperature": 0.7,
            },
        }

        # Construct API endpoint URL
        url = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{target_model}/invoke"

        try:
            # Make HTTP POST request
            response = requests.post(url, headers=headers, json=payload)

            # Check for HTTP errors
            response.raise_for_status()

            # Parse response JSON
            response_data = response.json()

            # Extract response text
            output_message = response_data["output"]["message"]
            assistant_text = output_message["content"][0]["text"]

            return assistant_text

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            error_text = e.response.text if e.response else str(e)
            raise RuntimeError(f"HTTP error ({status_code}): {error_text}")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {str(e)}")

        except KeyError as e:
            raise RuntimeError(f"Unexpected API response format: {str(e)}")

        except Exception as e:
            raise RuntimeError(f"Unexpected error calling Bedrock via HTTP: {str(e)}")


# Note: We'll instantiate this in chat.py after loading config
