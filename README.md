
# **Reusable LLM UI Project**

A project focused on building a **reusable front-end UI** that can work with any Large Language Model (LLM) backend.

---

## **Project Structure**

The UI is organized into two main components:

- **Front End**  
  Contains Jinja templates for rendering HTML, along with associated CSS and JavaScript files.

- **Back End**  
  FastAPI application that defines API endpoints and serves the front-end templates.
---

- **Note books**  
  Contains Jupyter notebooks to test Memory module of llama index. This memory module is required to convert a LLM into chatbot
  Apart from this Self discover agent has been tested in the notebooks. 

---

## **LLM Integration**

The project uses the `llama-index` framework to define and interact with LLMs. Currently, two LLM integrations are implemented:

- **Ollama**  
  Supports any LLM served locally via Ollama.

- **AWS Bedrock**  
  Connects to LLMs hosted on AWS Bedrock. The demo utilizes the `nova-lite` models.

---

## **Front-End Features**

- ChatGPT-style conversational UI with:
  - Input box (editable `div`) for entering text.  
    *(Supports images and files, though currently only text processing is implemented.)*  
  - Scrollable area for displaying chat history.
  - Sidebar for additional controls or information.

- **Markdown Parsing**  
  LLM responses are rendered using the `marked` JavaScript library for proper Markdown formatting.

- **Code Highlighting**  
  Code snippets in LLM responses are highlighted using `highlight.js`.

---

## **Future Improvements (Optional Section)**

- Image and file processing support in the input area.
- Additional LLM integrations.
- Improved error handling and UI enhancements.

---
