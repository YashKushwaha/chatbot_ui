from llama_index.core.memory import Memory
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.chat_engine import SimpleChatEngine

class CustomSimpleChatEngine(SimpleChatEngine):
    def __init__(self, llm, memory=None, prefix_messages=None):
        self.llm = llm
        self.abc = None




def get_simple_chat_engine(llm, memory=None, prefix_messages=None):
    memory = memory or Memory.from_defaults(token_limit=500)
    prefix_messages = prefix_messages or [ChatMessage(content="You are a helpful assistant.", role=MessageRole.SYSTEM)]
    chat_engine = SimpleChatEngine(llm=llm, memory=memory, prefix_messages=prefix_messages)
    return chat_engine