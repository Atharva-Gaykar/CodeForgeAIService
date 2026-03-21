from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
import os
from dotenv import load_dotenv
from langchain_community.retrievers import PineconeHybridSearchRetriever
import torch
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.schema import Document



device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": device})


load_dotenv()





PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "catalog-embeddings"


# Create index if not exists
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="dotproduct",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    print("Index created.")

index = pc.Index(index_name)
print("Index ready:", index.describe_index_stats())

bm25_encoder = BM25Encoder()

bm25_encoder.fit([doc.page_content for doc in documents])

retriever = PineconeHybridSearchRetriever(
    embeddings=embeddings,
    sparse_encoder=bm25_encoder,
    index=index
)
