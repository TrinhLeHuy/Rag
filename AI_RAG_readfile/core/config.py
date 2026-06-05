from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Tên của dự án
    PROJECT_NAME: str = "Dự án RAG Đa Dụng"
    
    # Chìa khóa (API Key) để gọi Groq. BẮT BUỘC phải tạo file tên '.env' và bỏ key vào đó, 
    # tuyệt đối không viết thẳng chữ "gsk_..." vào đây để tránh bị lộ mật khẩu.
    GROQ_API_KEY: str = "" 
    
    # --- Cài đặt Cloud Vector DB (Pinecone) ---
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "ttc-agris-reports"
    
    # Chuỗi kết nối đến cơ sở dữ liệu truyền thống (Database)
    DATABASE_URL: str = "sqlite:///./rag_database_v2.db"
    
    # --- Cài đặt cho việc cắt chữ (Chunking) ---
    CHUNK_SIZE: int = 1000 # Độ dài của mỗi mảnh văn bản
    CHUNK_OVERLAP: int = 200 # Độ dài phần lặp lại giữa 2 mảnh
    
    # --- Cài đặt cho việc tìm kiếm (Retrieval) ---
    RETRIEVER_K: int = 3 # Lấy ra 3 tài liệu liên quan nhất
    
    class Config:
        env_file = ".env"

settings = Settings()
