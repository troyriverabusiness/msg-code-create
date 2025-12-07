from typing import Optional
from server.data.AWS.bedrock_service import BedrockService
from server.data.AWS.config import (
    AWS_ACCESS_KEY,
    AWS_SECRET,
    AWS_REGION,
    AWS_SHORT_TERM_KEY,
    DEFAULT_SYSTEM_PROMPT,
)
from .session_manager import session_manager


if (not AWS_ACCESS_KEY or not AWS_SECRET) and not AWS_SHORT_TERM_KEY:
    raise ValueError(
        "AWS credentials not found in .env file. "
        "Please add AWS_ACCESS_KEY and AWS_SECRET OR AWS_SHORT_TERM_KEY to .env"
    )

bedrock_service = BedrockService(
    aws_access_key=AWS_ACCESS_KEY, aws_secret_key=AWS_SECRET, region=AWS_REGION
)


from .tools import TOOLS, execute_tool
import json

def chat(message: str, session_id: Optional[str] = None) -> tuple[str, str]:
    session = session_manager.get_or_create_session(session_id)
    # The history passed to bedrock_service.send_message needs to be just role/content strings
    # The session_manager's history is already in this format.
    
    current_message_for_llm = message # The message that will be sent to the LLM in the current turn

    try:
        # Tool Config
        tool_config = {"tools": TOOLS}
        
        response_data = None # Initialize response_data outside loop

        # 2. Handle Tool Use Loop (Max 3 turns)
        for turn_count in range(3):
            history_for_llm = session_manager.get_history(session.session_id) # Get fresh history
            
            response_data = bedrock_service.send_message(
                message=current_message_for_llm,
                conversation_history=history_for_llm,
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                tool_config=tool_config
            )
            
            if response_data["stop_reason"] == "tool_use":
                # Add assistant's tool-use response to session history
                # We convert the tool requests to a string representation for history
                assistant_tool_request_str = "Assistant requested tool execution: " + json.dumps(response_data["tool_requests"])
                session_manager.add_message(session.session_id, "assistant", assistant_tool_request_str)

                tool_results_summary = []
                for tool_req in response_data["tool_requests"]:
                    tool_name = tool_req["name"]
                    tool_args = tool_req["input"]
                    
                    print(f"Executing tool: {tool_name} with {tool_args}")
                    try:
                        result = execute_tool(tool_name, tool_args)
                        tool_results_summary.append(f"Tool '{tool_name}' result: {result}")
                    except Exception as e:
                        tool_results_summary.append(f"Tool '{tool_name}' failed: {str(e)}")
                
                # The tool results become the "user message" for the next LLM call
                current_message_for_llm = "Tool execution feedback: " + "\n".join(tool_results_summary)
                
            else: # Stop reason is 'end_turn' or other final reason
                # Final response from AI, add to history and return
                final_response_text = response_data["text"]
                session_manager.add_message(session.session_id, "user", message) # Original user message
                session_manager.add_message(session.session_id, "assistant", final_response_text) # Final AI response
                return final_response_text, session.session_id

        # If loop finishes (max turns reached) without a final answer
        # This implies the AI is stuck in a tool-use loop or failed to generate text.
        # We return the last generated text, or a generic error.
        final_response_text = "AI did not provide a final answer after multiple tool calls."
        if response_data and response_data.get("text"):
            final_response_text = response_data["text"]
        
        session_manager.add_message(session.session_id, "user", message)
        session_manager.add_message(session.session_id, "assistant", final_response_text)
        return final_response_text, session.session_id

    except RuntimeError as e:
        raise RuntimeError(f"Failed to get AI response: {str(e)}")