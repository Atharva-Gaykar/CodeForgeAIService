import json
import pickle
import requests
from pathlib import Path
from typing import List

from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from langchain_community.retrievers import PineconeHybridSearchRetriever
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.core.config import settings


# -----------------------------
# Paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "langchain_formatted.json"
BM25_PKL_PATH = BASE_DIR / "bm25.pkl"



# General Remote Embeddings
# avoids cold starts


class GeneralRemoteEmbeddings(Embeddings):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = requests.post(
            f"{self.endpoint}/embed_docs",
            json={"texts": texts}
        )
        response.raise_for_status()
        return response.json()["embeddings"]

    def embed_query(self, text: str) -> List[float]:
        response = requests.post(
            f"{self.endpoint}/embed_query",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]


embeddings = GeneralRemoteEmbeddings(
    endpoint="https://gaykar-generalembeddings.hf.space"
)


# -----------------------------
# Load Documents
# -----------------------------

def load_documents(data_path: Path) -> List[Document]:
    if not data_path.exists():
        raise FileNotFoundError(f"Catalog file not found: {data_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = [
        Document(
            page_content=doc["page_content"],
            metadata=doc["metadata"]
        )
        for doc in data
    ]

    print(f"Loaded {len(documents)} course documents")
    return documents


documents: List[Document] = load_documents(DATA_PATH)

if not documents:
    raise ValueError("No documents loaded from formatted_catalog.json")


# -----------------------------
# Pinecone Index
# -----------------------------

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

INDEX_NAME = "final-catalog-index"

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="dotproduct",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    print(f"Index created: {INDEX_NAME}")

index = pc.Index(INDEX_NAME)
print("Index ready:", index.describe_index_stats())


# -----------------------------
# BM25 Sparse Encoder
# Loads from pickle if exists, fits and saves if not
# -----------------------------

bm25_encoder = BM25Encoder()

if BM25_PKL_PATH.exists():
    print("Loading existing BM25 model from pickle...")
    with open(BM25_PKL_PATH, "rb") as f:
        bm25_encoder = pickle.load(f)
else:
    print("Fitting BM25 on course catalog...")
    bm25_encoder.fit([doc.page_content for doc in documents])
    with open(BM25_PKL_PATH, "wb") as f:
        pickle.dump(bm25_encoder, f)
    print(f"BM25 fitted and saved to {BM25_PKL_PATH}")


# -----------------------------
# Hybrid Retriever
# -----------------------------

retriever = PineconeHybridSearchRetriever(
    embeddings=embeddings,
    sparse_encoder=bm25_encoder,
    index=index
)

print("Retriever ready.")