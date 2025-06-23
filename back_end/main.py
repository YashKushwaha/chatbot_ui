import os
from pathlib import Path
import asyncio
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi import Request
from fastapi import Form, File, UploadFile

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from config_settings import *

class QueryRequest(BaseModel):
    message: str

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/chat_old"
    })

from llama_index.llms.ollama import Ollama
model = "phi4:latest"
context_window = 1000

llm = Ollama(
    model=model,
    request_timeout=120.0,
    context_window=context_window,
)


async  def dummy_llm_call(response):
    for word in response:
        yield word
        await asyncio.sleep(0.05)  # simulate delay

# Async generator wrapper for the streaming LLM response
async def stream_llm_response(prompt: str):
    response = llm.stream_complete(prompt)
    for chunk in response:
        yield chunk.delta
        await asyncio.sleep(0)  # Yield control to event loop


@app.post("/chat")
async def chat(message: str = Form(...), image: UploadFile = File(None)):
    #response = llm.stream_complete(message)
    return StreamingResponse(stream_llm_response(message), media_type="text/plain")

@app.post("/chat_old")
async def chat(message: str = Form(...), image: UploadFile = File(None)):
    print("Received message:", message)
    #return JSONResponse({"response": message})
    return StreamingResponse(dummy_llm_call(message), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True)