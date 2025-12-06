import inspect
from langchain_core.language_models.chat_models import BaseChatModel

print(f"Signature: {inspect.signature(BaseChatModel._generate)}")
