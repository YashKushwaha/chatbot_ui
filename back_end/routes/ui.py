from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import json
from back_end.config_settings import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/chat"
    })

@router.get("/chat_bot", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/chat_bot"
    })


@router.get("/chat_history", response_class=HTMLResponse)
def chat_history(request: Request):
    chat_history = request.app.state.chat_engine.chat_history

    return templates.TemplateResponse("chat_history_template.html", {
        "request": request,
        "chat_history": chat_history
    })

@router.get("/buffer_memory", response_class=HTMLResponse)
def chat_history(request: Request):
    chat_history = request.app.state.chat_engine._memory.get()

    return templates.TemplateResponse("chat_history_template.html", {
        "request": request,
        "chat_history": chat_history
    })

@router.get("/chat_history_raw", response_class=HTMLResponse)
def root(request: Request):
    chat_history = request.app.state.chat_engine.chat_history
    return json.dumps([msg.dict() for msg in chat_history], indent=2)

@router.get("/echo", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_endpoint": "/chat_old"
    })


@router.get("/vector_store/stats")
def vector_store_stats(request: Request):
    vector_store = request.app.state.index._vector_store
    collection = vector_store._collection  # Chroma collection
    
    total_vectors = collection.count()

    sample = collection.get(include=["documents", "metadatas"], limit=2)
    items = [
        {"id": id_, "document": doc, "metadata": meta}
        for id_, doc, meta in zip(sample["ids"], sample["documents"], sample["metadatas"])
    ]

    return {
        "total_vectors": total_vectors,
        "sample_items": items
    }
