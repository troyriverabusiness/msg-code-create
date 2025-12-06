import asyncio
import os
import sys
from server.agent.core import get_agent_executor

async def main():
    print("🤖 Travel Assistant CLI (Type 'quit' to exit)")
    print("-" * 40)
    
    # Check for credentials
    if not os.environ.get("DB_CLIENT_ID") or not os.environ.get("DB_API_KEY"):
        print("⚠️  WARNING: DB_CLIENT_ID or DB_API_KEY not set. Live data tools will fail.")
    
    try:
        agent = get_agent_executor()
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        print("Agent: Thinking...", end="\r")
        
        try:
            response = await agent.ainvoke({"messages": [{"role": "user", "content": user_input}]})
            print(f"Agent: {response['messages'][-1].content}")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
