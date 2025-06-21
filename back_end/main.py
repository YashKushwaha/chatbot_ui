import os
from pathlib import Path

from pydantic import BaseModel

from fastapi import FastAPI
from fastapi import Request
from fastapi import Form, File, UploadFile

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

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
        "chat_endpoint": "/chat"
    })


@app.post("/chat")
async def chat(message: str = Form(...), image: UploadFile = File(None)):
    print("Received message:", message)

    # Sample markdown content
    response = """
## 🤖 Chatbot Response

Hello! You said: **Hi**

Here's a sample **Python** snippet:

```python
import pandas as pd

def greet(name):
    return f"Hello!"
```

We can also show some **JSON**:

```json
{
  "name": "ChatGPT",
  "language": "Python",
  "version": 4.0
}
```

- This is a bullet list
- With **bold** text
- And *italicized* items

> This is a blockquote.

Inline code looks like this: `print("Hello")`

Thanks for testing!
"""

    return JSONResponse({"response": response})


if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True)