# pipeline/vectorstore.py — ChromaDB persistent vector store
import os
import uuid

import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chromadb")

COMPANY_CONTEXT = "company_context"
REPORT_HISTORY = "report_history"
FEEDBACK_DIGESTS = "feedback_digests"

_embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

_client = None


def get_client():
    global _client
    if _client is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=DATA_DIR)
    return _client


def get_collection(name):
    client = get_client()
    return client.get_or_create_collection(name=name, embedding_function=_embedding_function)


def add_documents(collection_name, documents, metadatas=None, ids=None):
    collection = get_collection(collection_name)
    if ids is None:
        ids = [str(uuid.uuid4()) for _ in documents]
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return ids


def query(collection_name, query_text, n_results=5):
    collection = get_collection(collection_name)
    return collection.query(query_texts=[query_text], n_results=n_results)


def delete_documents(collection_name, ids):
    collection = get_collection(collection_name)
    collection.delete(ids=ids)
