
from pathlib import Path
import os
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from datasets import load_dataset
import chromadb

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def load_squad_documents(max_docs=50, download_location=None):
    dataset = load_dataset("rajpurkar/squad_v2", cache_dir=download_location)
    print('SQUAD data will be downloaded to ', download_location)
    documents = []
    for i in dataset['train'].select(range(max_docs)):
        item = dict(i)
        context = item.pop('context')
        metadata  = item
        documents.append(Document(text=context, metadata=metadata))

    return documents

def create_vector_index(documents, embed_model, vec_store_location):
    os.makedirs(vec_store_location, exist_ok=True)
    db_exists = Path(vec_store_location).exists()

    db = chromadb.PersistentClient(path=vec_store_location)
    chroma_collection = db.get_or_create_collection("my_collection")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    if db_exists:
        print("✅ Existing Chroma DB found, loading index...")
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context,
            embed_model=embed_model
        )
    else:
        print("🆕 No existing DB found, creating new index...")
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=embed_model
        )
        storage_context.persist(vec_store_location)
    return index


if __name__ == '__main__':
    
    CACHE_DIR = os.path.join(Path(__file__).resolve().parents[1] , "local_only", "data")
    os.makedirs(CACHE_DIR, exist_ok=True)
    documents = load_squad_documents(download_location = CACHE_DIR)
    print('Num documents ->', len(documents))

    vec_store_location = os.path.join(Path(__file__).resolve().parents[1] , "local_only", "vector store")   
    os.makedirs(vec_store_location, exist_ok=True) 
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index = create_vector_index(documents, embed_model, vec_store_location)
    print('Done')