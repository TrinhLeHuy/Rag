from langchain_pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from core.config import settings
import os

# Set API Key cho Pinecone qua env var VÀ truyền trực tiếp
os.environ["PINECONE_API_KEY"] = settings.PINECONE_API_KEY

def get_vectorstore():
    # Sử dụng mô hình nhúng BGE-M3 (Enterprise-grade)
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    # Trỏ đến Cloud Vector DB, truyền pinecone_api_key trực tiếp
    vectorstore = Pinecone(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings,
        pinecone_api_key=settings.PINECONE_API_KEY,
    )
    return vectorstore

def add_documents_to_cloud_db(chunks):
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
