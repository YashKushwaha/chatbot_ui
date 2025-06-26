
from pathlib import Path
import os
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from datasets import load_dataset
import chromadb

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def process_squad_item(item):
    # Extract context
    context = item.pop("context")

    # Flatten answers dictionary
    answers_dict = item.get("answers", {})
    flat_answers = "; ".join(answers_dict.get("text", []))
    first_answer_start = (
        answers_dict.get("answer_start", [None])[0]
        if answers_dict.get("answer_start")
        else None
    )

    # Prepare flat metadata
    metadata = {
        "id": item.get("id"),
        "title": item.get("title"),
        "question": item.get("question"),
        "answers": flat_answers,
        "answer_start": first_answer_start
    }

    return Document(text=context, metadata=metadata)

def load_squad_documents(max_docs=50, download_location=None):
    dataset = load_dataset("rajpurkar/squad_v2", cache_dir=download_location)
    print('SQUAD data will be downloaded to ', download_location)
    documents = []
    for i in dataset['train'].select(range(max_docs)):
        """
        item = dict(i)
        context = item.pop('context')
        metadata  = item
        documents.append(Document(text=context, metadata=metadata))
        """
        
        
        document = process_squad_item(i)
        documents.append(document)

    return documents

def create_vector_index(documents, embed_model, vec_store_location):
    os.makedirs(vec_store_location, exist_ok=True)
    db_exists = Path(vec_store_location).exists()

    db = chromadb.PersistentClient(path=vec_store_location)
    chroma_collection = db.get_or_create_collection("my_collection")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    if chroma_collection.count() == 0:
        print("No vectors found. Creating new index...")
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)
    else:
        print(f"Loaded existing collection with {chroma_collection.count()} vectors.")
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context, embed_model=embed_model)
   
    return index

def get_index_from_squad_dataset(embed_model):
    CACHE_DIR = os.path.join(Path(__file__).resolve().parents[1] , "local_only", "data")
    os.makedirs(CACHE_DIR, exist_ok=True)
    documents = load_squad_documents(download_location = CACHE_DIR)
    print('Num documents ->', len(documents))

    vec_store_location = os.path.join(Path(__file__).resolve().parents[1] , "local_only", "vector_store")   
    os.makedirs(vec_store_location, exist_ok=True) 
    
    index = create_vector_index(documents, embed_model, vec_store_location)
    return index

if __name__ == '__main__':
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index =get_index_from_squad_dataset(embed_model)
    print('Done')