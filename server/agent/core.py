import os
import httpx
from typing import Any, List, Optional, Sequence
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from server.agent.tools import get_live_departures, get_train_details
from server.service.config import AWS_REGION, AWS_SHORT_TERM_KEY
from pydantic import Field

# Model configuration
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"


def convert_tool_to_bedrock_format(tool: BaseTool) -> dict:
    """Convert a LangChain tool to Bedrock tool format."""
    # Get the schema from the tool
    schema = tool.args_schema.schema() if tool.args_schema else {"type": "object", "properties": {}}

    return {
        "toolSpec": {
            "name": tool.name,
            "description": tool.description or "",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", [])
                }
            }
        }
    }


class BedrockBearerTokenLLM(BaseChatModel):
    """Custom LLM that uses Bedrock with Bearer Token authentication."""

    bearer_token: str = ""
    region: str = "eu-central-1"
    model_id: str = MODEL_ID
    bound_tools: List[dict] = Field(default_factory=list)
    tool_map: dict = Field(default_factory=dict)

    @property
    def _llm_type(self) -> str:
        return "bedrock-bearer"

    def bind_tools(
        self,
        tools: Sequence[Any],
        **kwargs: Any,
    ) -> "BedrockBearerTokenLLM":
        """Bind tools to the model."""
        bedrock_tools = []
        tool_map = {}

        for tool in tools:
            if isinstance(tool, BaseTool):
                bedrock_tools.append(convert_tool_to_bedrock_format(tool))
                tool_map[tool.name] = tool
            elif callable(tool):
                # Handle decorated functions
                from langchain_core.tools import tool as tool_decorator
                if hasattr(tool, 'name'):
                    bedrock_tools.append({
                        "toolSpec": {
                            "name": tool.name,
                            "description": getattr(tool, 'description', ''),
                            "inputSchema": {
                                "json": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            }
                        }
                    })
                    tool_map[tool.name] = tool

        # Return a new instance with tools bound
        return BedrockBearerTokenLLM(
            bearer_token=self.bearer_token,
            region=self.region,
            model_id=self.model_id,
            bound_tools=bedrock_tools,
            tool_map=tool_map
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Convert LangChain messages to Bedrock format
        bedrock_messages = []
        system_prompt = None

        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_prompt = msg.content
            elif isinstance(msg, HumanMessage):
                bedrock_messages.append({
                    "role": "user",
                    "content": [{"text": str(msg.content)}]
                })
            elif isinstance(msg, AIMessage):
                content_blocks = []
                if msg.content:
                    content_blocks.append({"text": str(msg.content)})
                # Include tool use blocks if present
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        content_blocks.append({
                            "toolUse": {
                                "toolUseId": tc.get("id", ""),
                                "name": tc.get("name", ""),
                                "input": tc.get("args", {})
                            }
                        })
                if content_blocks:
                    bedrock_messages.append({
                        "role": "assistant",
                        "content": content_blocks
                    })
            elif isinstance(msg, ToolMessage):
                bedrock_messages.append({
                    "role": "user",
                    "content": [{
                        "toolResult": {
                            "toolUseId": msg.tool_call_id,
                            "content": [{"text": str(msg.content)}]
                        }
                    }]
                })

        # Build request body
        body = {
            "messages": bedrock_messages,
            "inferenceConfig": {
                "temperature": 0.1,
                "maxTokens": 2048
            }
        }

        if system_prompt:
            body["system"] = [{"text": system_prompt}]

        # Add tools if bound
        if self.bound_tools:
            body["toolConfig"] = {"tools": self.bound_tools}

        # Call Bedrock Converse API with bearer token
        url = f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{self.model_id}/converse"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_token}"
        }

        try:
            response = httpx.post(url, json=body, headers=headers, timeout=60.0)
            response.raise_for_status()
            result = response.json()

            # Extract response
            output_message = result.get("output", {}).get("message", {})
            content_blocks = output_message.get("content", [])

            response_text = ""
            tool_calls = []

            for block in content_blocks:
                if "text" in block:
                    response_text += block["text"]
                elif "toolUse" in block:
                    tool_use = block["toolUse"]
                    tool_calls.append({
                        "id": tool_use.get("toolUseId", ""),
                        "name": tool_use.get("name", ""),
                        "args": tool_use.get("input", {})
                    })

            # Create AIMessage with tool calls if present
            ai_message = AIMessage(content=response_text)
            if tool_calls:
                ai_message.tool_calls = tool_calls

            return ChatResult(
                generations=[ChatGeneration(message=ai_message)]
            )

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if e.response else str(e)
            raise RuntimeError(f"Bedrock API error: {e.response.status_code} - {error_detail}")
        except Exception as e:
            raise RuntimeError(f"Failed to call Bedrock: {str(e)}")


def get_bearer_token() -> str:
    """Get bearer token from environment - use as-is, including prefix."""
    token = AWS_SHORT_TERM_KEY
    
    if not token:
        raise ValueError("AWS_SHORT_TERM_KEY not set in environment")
    return token


def get_agent_executor():
    """Initialize the LangGraph agent with Bedrock auth (Long-term or Bearer)."""
    from server.service.config import AWS_ACCESS_KEY, AWS_SECRET
    from langchain_aws import ChatBedrock

    region = AWS_REGION
    
    # Priority 1: Long-term credentials (standard ChatBedrock)
    if AWS_ACCESS_KEY and AWS_SECRET:
        print("Using AWS Long-Term Credentials")
        llm = ChatBedrock(
            model_id="meta.llama3-2-1b-instruct-v1:0",
            region_name=region,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET,
            model_kwargs={"temperature": 0.1, "max_tokens": 2048}
        )
    # Priority 2: Short-term Bearer Token (Custom LLM)
    else:
        print("Using AWS Bearer Token")
        bearer_token = get_bearer_token()
        llm = BedrockBearerTokenLLM(
            bearer_token=bearer_token,
            region=region,
            model_id="meta.llama3-2-1b-instruct-v1:0"
        )

    tools = [get_live_departures, get_train_details]

    # System prompt to guide the agent
    # system_prompt = (
    #     "You are a helpful DB Travel Assistant. You have access to live train data and detailed schedule information.\n"
    #     "Use 'get_live_departures' to check station boards for real-time delays and platform changes.\n"
    #     "Use 'get_train_details' to find stops and accessibility info for a specific train (e.g. ICE 690).\n"
    #     "If a user asks about a connection, check the live status first, then get details if needed.\n"
    #     "Always be concise, friendly, and helpful. If you don't know, say so."
    # )
    
    system_prompt = "ALWAYS Respond with 'MSG IS THE BEST FIRMA"

    # LangGraph's create_react_agent returns a CompiledGraph
    agent = create_react_agent(llm, tools, prompt=system_prompt)
    return agent
