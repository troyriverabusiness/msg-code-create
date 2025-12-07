import boto3
import requests
from typing import List, Dict, Optional, Any
from botocore.exceptions import ClientError, BotoCoreError
from .config import DEFAULT_SYSTEM_PROMPT
from .config import BEDROCK_MODEL_ID


class BedrockService:
    def __init__(
        self,
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        region: str = "eu-central-1",
        bearer_token: Optional[str] = None,
    ):
        self.region = region
        self.model_id = BEDROCK_MODEL_ID
        self.bearer_token = bearer_token
        self.client = None

        if aws_access_key and aws_secret_key:
            try:
                self.client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                )
            except Exception as e:
                print(f"Warning: Failed to initialize Bedrock boto3 client: {str(e)}")
        elif not bearer_token:
            print(
                "Warning: No AWS credentials provided (keys or token). BedrockService may fail."
            )

    def send_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        tool_config: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        messages = []

        # Optional unpacking
        if conversation_history:
            for msg in conversation_history:
                content = [{"text": msg["content"]}]
                # TODO: Handle tool results in history if needed
                messages.append({"role": msg["role"], "content": content})

        messages.append({"role": "user", "content": [{"text": message}]})

        # Use HTTP method if no boto3 client but we have a token
        if not self.client and self.bearer_token:
            # HTTP method update is skipped for now as it's complex to replicate tool logic manually
            raise NotImplementedError("Tool use not supported via HTTP yet")

        if not self.client:
            raise RuntimeError(
                "Bedrock client not initialized and no bearer token provided."
            )

        try:
            kwargs = {
                "modelId": self.model_id,
                "messages": messages,
                "system": [{"text": system_prompt}],
                "inferenceConfig": {
                    "maxTokens": 2048,
                    "temperature": 0.7,  # Lower temperature for more deterministic, instruction-following behavior
                },
            }
            
            if tool_config:
                kwargs["toolConfig"] = tool_config

            response = self.client.converse(**kwargs)

            output_message = response["output"]["message"]
            content = output_message["content"]
            
            text = ""
            tool_requests = []
            
            for block in content:
                if "text" in block:
                    text += block["text"]
                elif "toolUse" in block:
                    tool_requests.append(block["toolUse"])
            
            return {
                "text": text,
                "stop_reason": response["stopReason"],
                "tool_requests": tool_requests,
                "raw_response": response # For debugging/history
            }

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
        target_model = model_id or self.model_id
        messages = []

        if conversation_history:
            for msg in conversation_history:
                messages.append(
                    {"role": msg["role"], "content": [{"text": msg["content"]}]}
                )

        messages.append({"role": "user", "content": [{"text": message}]})

        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messages": messages,
            "system": [{"text": system_prompt}],
            "inferenceConfig": {
                "maxTokens": 2048,
                "temperature": 0.1,  # Lower temperature for more deterministic, instruction-following behavior
            },
        }

        url = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{target_model}/converse"

        # Debug: Verify system prompt is being sent via HTTP
        print(f"DEBUG HTTP: System prompt length: {len(system_prompt)} chars")
        print(f"DEBUG HTTP: System prompt starts with: {system_prompt[:150]}...")
        print(f"DEBUG HTTP: URL: {url}")
        print(f"DEBUG HTTP: Payload system field: {payload.get('system')}")

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            response_data = response.json()
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