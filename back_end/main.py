import os
print(os.getcwd())

from pathlib import Path
import asyncio
from pydantic import BaseModel
import boto3
import botocore.session

from fastapi import FastAPI
from fastapi import Request
from fastapi import Form, File, UploadFile

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse


import json
from llama_index.llms.bedrock_converse import BedrockConverse

from src.config_loader import get_config, load_env_vars
from src.chat_engines import (get_simple_chat_engine, get_condense_question_chat_engine, 
                get_context_chat_engine, get_condense_plus_context_chat_engine)

from config_settings import *

# Load config + .env
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


class QueryRequest(BaseModel):
    message: str

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/chat"
    })

@app.get("/chat_bot", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/chat_bot"
    })


@app.get("/chat_history", response_class=HTMLResponse)
def chat_history(request: Request):
    chat_history = app.state.chat_engine.chat_history

    return templates.TemplateResponse("chat_history_template.html", {
        "request": request,
        "chat_history": chat_history
    })

@app.get("/buffer_memory", response_class=HTMLResponse)
def chat_history(request: Request):
    chat_history = app.state.chat_engine._memory.get()

    return templates.TemplateResponse("chat_history_template.html", {
        "request": request,
        "chat_history": chat_history
    })

@app.get("/chat_history_raw", response_class=HTMLResponse)
def root(request: Request):
    chat_history = app.state.chat_engine.chat_history
    return json.dumps([msg.dict() for msg in chat_history], indent=2)

@app.get("/echo", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/chat_old"
    })

from llama_index.llms.ollama import Ollama

model = "phi4:latest"
context_window = 1000

ollama_llm = Ollama(
    model=model,
    request_timeout=120.0,
    context_window=context_window,
)

llm = ollama_llm
#llm = bedrock_llm

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

chat_engine = get_condense_plus_context_chat_engine(llm)

app.state.chat_engine  = chat_engine

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