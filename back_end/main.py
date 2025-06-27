import os

from pathlib import Path
import asyncio
from pydantic import BaseModel
from pydantic import PrivateAttr

import boto3
import botocore.session
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from fastapi import FastAPI
from fastapi import Request
from fastapi import Form, File, UploadFile

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from llama_index.core.callbacks.base import BaseCallbackHandler, CBEventType
from llama_index.core.callbacks import CallbackManager

from llama_index.core.instrumentation.event_handlers.base import BaseEventHandler
from llama_index.core.instrumentation.events.base import BaseEvent

from llama_index.llms.bedrock_converse import BedrockConverse

from llama_index.core import ServiceContext

from src.config_loader import get_config, load_env_vars
from src.chat_engines import (get_simple_chat_engine, get_condense_question_chat_engine, 
                get_context_chat_engine, get_condense_plus_context_chat_engine)

from config_settings import *

from scripts.data_loader import get_index_from_squad_dataset
from routes import ui

debug_logs = []

import mlflow

log_folder = os.path.join(PROJECT_ROOT, 'mlflow_logs')
os.makedirs(log_folder, exist_ok=True)
mlflow.set_tracking_uri(log_folder)
mlflow.set_experiment("chatbot_debug_logs")
mlflow.llama_index.autolog()  # Enable mlflow tracing

from llama_index.core.instrumentation.event_handlers.base import BaseEventHandler
from llama_index.core.instrumentation.events.base import BaseEvent

class MyDebugHandler(BaseEventHandler):
    """Tracks events for debugging."""

    _logs: list = PrivateAttr(default_factory=list)  # Private mutable field

    @classmethod
    def class_name(cls) -> str:
        return "MyDebugHandler"

    def handle(self, event: BaseEvent, **kwargs):
        log_entry = {
            "event": event.class_name(),
            "payload": event.payload,
        }
        print(f"[DEBUG] {log_entry}")  # Optional console log
        self._logs.append(log_entry)

    def get_logs(self):
        return self._logs

from llama_index.core import Settings
from llama_index.core.instrumentation.dispatcher import Dispatcher
"""
debug_handler = MyDebugHandler()
dispatcher = Dispatcher()
dispatcher.add_event_handler(debug_handler)
Settings.dispatcher = dispatcher
"""

def get_bedrock_llm():
    config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    config = get_config(config_path)
    load_env_vars(config)
    #session = boto3.Session()  # uses env vars from .env.aws
    botocore_session = botocore.session.get_session()
    #https://github.com/run-llama/llama_index/blob/main/llama-index-integrations/llms/llama-index-llms-bedrock/llama_index/llms/bedrock/base.py

    MODEL_ID = 'arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0'
    MAX_TOKENS = 512
    TEMPERATURE = 0.7
    TOP_P = 0.9
    CONTEXT_SIZE = 512 # max length of input
    init_args = dict(model=MODEL_ID, temperature= TEMPERATURE, max_tokens = MAX_TOKENS)
    bedrock_llm = BedrockConverse(botocore_session = botocore_session, **init_args)
    return bedrock_llm

class QueryRequest(BaseModel):
    message: str

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

app.include_router(ui.router)

# Setup callback manager
#debug_handler = DebugHandler()
#callback_manager = CallbackManager([debug_handler])

from llama_index.llms.ollama import Ollama

model = "phi4:latest"
context_window = 1000

ollama_llm = Ollama(
    model=model,
    request_timeout=120.0,
    context_window=context_window,
)

llm = ollama_llm
#llm = get_bedrock_llm()

async  def dummy_llm_call(response):
    for word in response:
        yield word
        await asyncio.sleep(0.05)  # simulate delay

# Async generator wrapper for the streaming LLM response
async def stream_llm_response(llm, prompt: str):
    response = llm.stream_complete(prompt)
    for chunk in response:
        yield chunk.delta
        await asyncio.sleep(0.1)

async def stream_llm_chat_response(llm, prompt: str):
    response = llm.astream_chat(prompt)
    for chunk in response:
        yield chunk.delta
        await asyncio.sleep(0.1)

#app.state.chat_engine = get_simple_chat_engine(llm)
#chat_engine = get_condense_question_chat_engine(llm)
#chat_engine = get_context_chat_engine(llm)

Settings.llm = llm

embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
index = get_index_from_squad_dataset(embed_model)
chat_engine = get_context_chat_engine(llm, index)

app.state.chat_engine  = chat_engine
app.state.embed_model  = embed_model
app.state.index = index 

@app.get("/vector_store/stats")
def vector_store_stats():
    vector_store = app.state.index._vector_store
    collection = vector_store._collection  # Chroma collection
    
    total_vectors = collection.count()
    sample = collection.get(include=["documents", "metadatas"], limit=5)
    
    items = [
        {"id": id_, "document": doc, "metadata": meta}
        for id_, doc, meta in zip(sample["ids"], sample["documents"], sample["metadatas"])
    ]
    
    return {
        "total_vectors": total_vectors,
        "sample_items": items
    }

@app.post("/chat_bot")
async def chat(message: str = Form(...), image: UploadFile = File(None)):
    chat_engine = app.state.chat_engine
    response = chat_engine.stream_chat(message=message)
    return StreamingResponse(response.response_gen, media_type="text/plain")

@app.post("/chat")
async def chat(message: str = Form(...), image: UploadFile = File(None)):
    return StreamingResponse(stream_llm_response(llm, message), media_type="text/plain")

@app.post("/chat_old")
async def chat(message: str = Form(...), image: UploadFile = File(None)):
    print("Received message:", message)
    #return JSONResponse({"response": message})
    return StreamingResponse(dummy_llm_call(message), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True)