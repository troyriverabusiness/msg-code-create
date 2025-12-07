
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from server.service.chat import chat

async def test_chat_via():
    prompt = "München Hbf nach Frankfurt Hbf über Stuttgart Hbf mit 180 Minuten Aufenthalt, morgen um 08:00 Uhr"
    print(f"Testing prompt: '{prompt}'")
    
    try:
        # chat is synchronous
        response = chat(prompt)
        print("\nResponse:")
        print(response)
        
        # We can't easily assert the internal tool call arguments here without mocking,
        # but we can check if the response mentions the connection details we expect.
        # Ideally, we'd see a journey with a transfer > 3 hours.
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_via())
