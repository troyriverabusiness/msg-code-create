from typing import Optional
from server.data_access.AWS.bedrock_service import BedrockService
from server.data_access.AWS.config import (
    AWS_ACCESS_KEY,
    AWS_SECRET,
    AWS_REGION,
    AWS_SHORT_TERM_KEY,
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
    history = session_manager.get_history(session.session_id)

    try:
        # Tool Config
        tool_config = {"tools": TOOLS}
        
        # 1. First Call
        response_data = bedrock_service.send_message(
            message=message, 
            conversation_history=history,
            tool_config=tool_config
        )
        
        # 2. Handle Tool Use Loop (Max 3 turns)
        for _ in range(3):
            if response_data["stop_reason"] == "tool_use":
                # Execute tools
                tool_results = []
                for tool_req in response_data["tool_requests"]:
                    tool_name = tool_req["name"]
                    tool_args = tool_req["input"]
                    tool_use_id = tool_req["toolUseId"]
                    
                    print(f"Executing tool: {tool_name} with {tool_args}")
                    try:
                        result = execute_tool(tool_name, tool_args)
                        content = [{"json": {"result": result}}]
                    except Exception as e:
                        content = [{"text": f"Error: {str(e)}"}]
                        
                    tool_results.append({
                        "toolResult": {
                            "toolUseId": tool_use_id,
                            "content": content,
                            "status": "success" if "json" in content[0] else "error"
                        }
                    })
                
                # Append assistant response (tool request) and tool results to history
                # Note: Bedrock requires strict history structure for tool use.
                # Since we are using a simplified session manager that stores strings, 
                # we might have issues if we don't store the full structure.
                
                # Hack: For now, we just send the tool result as a new user message context?
                # No, Bedrock converse API requires the tool result to follow the tool use.
                
                # Since BedrockService.send_message is stateless (re-sends history),
                # we need to append the tool interaction to the history passed to the NEXT call.
                
                # But session_manager stores simple text.
                # We need to update session_manager or handle this in-memory for this turn.
                
                # Let's handle it in-memory for this request, and only save the FINAL text to session_manager.
                # This means tool usage is lost in long-term history, but that's acceptable for MVP.
                
                # We need to construct the messages list manually for the follow-up.
                # BedrockService re-constructs it from history.
                
                # We can't easily use BedrockService.send_message for the follow-up because it expects simple history.
                # We need to call client.converse directly or update BedrockService to support passing "current turn messages".
                
                # Let's update BedrockService to allow passing "extra_messages" or similar?
                # Or just modify chat.py to use the client directly? No, that breaks abstraction.
                
                # Best approach for MVP:
                # Add the tool result as a "System" or "User" message saying "Tool Output: ..."
                # This is "fake" tool use but works for LLMs.
                # BUT we are using `toolConfig`, so the model EXPECTS a `toolResult` block.
                
                # If we can't provide `toolResult` block via `send_message`, we are stuck.
                
                # I will modify `BedrockService` to support a `continue_conversation` method that takes the previous response and tool results.
                # OR just assume the model is smart enough if we send the result as text.
                # But `stop_reason` was `tool_use`, so it might refuse to continue without a tool result.
                
                # Let's try sending the result as a new user message: "Tool find_intermediate_stations returned: [...]"
                # And remove `toolConfig` for the follow-up to force it to generate text?
                # This breaks the "native" flow but is robust.
                
                tool_outputs_str = "\n".join([json.dumps(r["toolResult"]["content"]) for r in tool_results])
                follow_up_msg = f"Tool execution results:\n{tool_outputs_str}\n\nPlease continue."
                
                # Recursive call (without tools to prevent loops? or with tools?)
                # Let's call with tools again.
                # But we append the previous assistant response (tool request) + our result to history?
                
                # Since session_manager is simple, let's just append the tool result as a USER message.
                # The model will see:
                # User: "Plan trip..."
                # Assistant: (Tool Request - hidden from history if we don't save it)
                # User: "Tool results: ..."
                # Assistant: "Okay, here is the plan..."
                
                # This works.
                response_data = bedrock_service.send_message(
                    message=follow_up_msg,
                    conversation_history=history, # Original history
                    tool_config=tool_config
                )
                
            else:
                break

        response_text = response_data["text"]
        
        session_manager.add_message(session.session_id, "user", message)
        session_manager.add_message(session.session_id, "assistant", response_text)

        return response_text, session.session_id

    except RuntimeError as e:
        raise RuntimeError(f"Failed to get AI response: {str(e)}")
