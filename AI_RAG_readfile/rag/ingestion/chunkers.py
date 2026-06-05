from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

def split_documents_semantically(documents):
    # Khởi tạo mô hình Embedding tốc độ cao để làm thước đo ngữ nghĩa
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    
    text_splitter = SemanticChunker(embeddings)
    chunks = text_splitter.split_documents(documents)
    return chunks
