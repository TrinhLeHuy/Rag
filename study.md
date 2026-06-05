# Sổ Tay Lập Trình Enterprise RAG - Phiên Bản Dành Cho Doanh Nghiệp

Tài liệu này hướng dẫn chi tiết cách xây dựng hệ thống **Enterprise RAG (Retrieval-Augmented Generation)**. Thay vì upload file thủ công và lưu trữ cơ sở dữ liệu trên máy cá nhân, hệ thống này được thiết kế để tự động cào dữ liệu từ Web (Web Crawling), chia nhỏ văn bản thông minh (Semantic Chunking) và lưu trữ trên Cloud Vector Database (Pinecone) để đảm bảo tính mở rộng và tốc độ cho doanh nghiệp.

Mục tiêu là giúp bạn xây dựng một dự án RAG tự động thu thập Báo cáo Phát triển Bền vững (ví dụ từ TTC AgriS) và cho phép người dùng hỏi đáp trực tiếp.

---
### 📖 Từ Điển Thuật Ngữ Enterprise RAG
- **Web Crawler / Scraper**: Công cụ tự động đi vào một đường link (URL) trang web, ví dụ như trang báo cáo của TTC AgriS, để thu thập nội dung bài viết hoặc tải các file PDF báo cáo được đính kèm.
- **Cloud Vector Database (Pinecone, Milvus)**: Cơ sở dữ liệu Vector lưu trữ trên đám mây (Cloud). Không cần tạo thư mục lưu trữ trên máy tính của bạn, giúp tìm kiếm siêu tốc độ (dưới 10ms) cho dữ liệu cực lớn.
- **Semantic Chunking (Chia văn bản theo ngữ nghĩa)**: Thay vì cắt văn bản một cách cơ học mỗi 1000 chữ (Recursive Chunking), hệ thống AI sẽ đọc và cắt văn bản thành từng đoạn sao cho mỗi đoạn giữ trọn vẹn một ý nghĩa.
- **Embedding Model**: Mô hình biến chữ thành số. Ở bản Enterprise, chúng ta có thể dùng OpenAI `text-embedding-3` hoặc các mô hình open-source mạnh như `BGE-M3`.

---

## 1. Thư mục `core/` (Cấu hình lõi)
Nơi chứa cài đặt chung. Ta loại bỏ các đường dẫn lưu trữ local và thêm API Key cho Cloud Vector DB (Pinecone).

**File: `core/config.py`**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise RAG System"
    
    # API Key của LLM (VD: Groq, OpenAI)
    GROQ_API_KEY: str = "" 
    
    # --- Cài đặt Cloud Vector DB (Pinecone) ---
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "ttc-agris-reports"
    
    # Chuỗi kết nối Database truyền thống (Lưu lịch sử chat & log cào dữ liệu)
    DATABASE_URL: str = "sqlite:///./rag_database.db"
    
    # --- Cài đặt Chunking nâng cao ---
    # Trong bản Enterprise ta dùng Semantic Chunking, không cần fix cứng CHUNK_SIZE
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 2. Thư mục `api/` (Giao diện API)
Thay vì API `/upload`, hệ thống Enterprise sẽ có API `/crawl` để nhận URL và tự động cào dữ liệu.

**File: `api/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, crawler, auth
from core.config import settings
from db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(crawler.router, prefix="/api/crawler", tags=["Web Crawler"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
```

**File: `api/routes/crawler.py` (MỚI)**
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from services.crawler_service import process_url_crawl
from db.database import get_db

router = APIRouter()

# Dữ liệu truyền vào là một URL thay vì File
class CrawlRequest(BaseModel):
    # Sử dụng báo cáo của TTC AgriS làm ví dụ mặc định
    url: str = "https://ttcagris.com.vn/media/sustainability-report/Bao_cao_PTBV_2425.pdf"

@router.post("/")
async def crawl_website(req: CrawlRequest, db: Session = Depends(get_db)):
    try:
        # Gọi Service để bắt đầu quá trình đi vào URL cào dữ liệu (ETL Pipeline)
        result_message = await process_url_crawl(req.url, db)
        return {"message": result_message, "url": req.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi crawl dữ liệu: {str(e)}")
```

---

## 3. Thư mục `db/` (Cơ Sở Dữ Liệu Truyền Thống)
Lưu lịch sử cào dữ liệu (CrawlRecord) thay cho lịch sử Upload (DocumentRecord).

**File: `db/models.py`**
```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from db.database import Base

# Bảng lưu trữ trạng thái Crawler
class CrawlRecord(Base):
    __tablename__ = "crawl_records"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True) 
    start_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="processing") # processing, success, failed

# Bảng lưu lịch sử chat và User giữ nguyên như bản cũ
class ChatHistory(Base):
    __tablename__ = "chat_histories"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_message = Column(Text)
    ai_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
```

---

## 4. Thư mục `rag/` (Khối Xử Lý Enterprise RAG)

### 4.1. Khối Tự Động Thu Thập (Data Ingestion & Pipeline)
Thay vì đọc file local, ta dùng `WebBaseLoader` (BeautifulSoup) hoặc công cụ Crawl để kéo nội dung trang web. Nếu trang web có file PDF, ta dùng `PyPDFLoader` kèm đường dẫn.

**File: `rag/ingestion/loaders.py`**
```python
from langchain_community.document_loaders import WebBaseLoader
import bs4

def scrape_website(url: str):
    """
    Sử dụng WebBaseLoader để quét nội dung. 
    Lọc bỏ Header/Footer/Ads, chỉ lấy phần nội dung chính (ví dụ thẻ article hoặc main).
    """
    # Cấu hình bs_kwargs để nhắm thẳng vào class chứa nội dung báo cáo
    loader = WebBaseLoader(
        web_paths=(url,),
        # Tùy chỉnh parser nếu cần lấy cụ thể class, ví dụ lấy text từ các bài viết
        # bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=("post-content", "main-body")))
    )
    docs = loader.load()
    return docs
```

**File: `rag/ingestion/chunkers.py`**
Áp dụng chiến lược chia nhỏ văn bản chuyên nghiệp: Semantic Chunking.
```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

def split_documents_semantically(documents):
    """
    Cắt văn bản thông minh dựa trên ngữ nghĩa (Semantic Chunking).
    Đoạn nào chung một ý sẽ được gom lại thay vì bị cắt gãy khúc.
    """
    # Khởi tạo mô hình Embedding tốc độ cao (BGE-M3 hoặc MiniLM) để làm thước đo ngữ nghĩa
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    
    text_splitter = SemanticChunker(embeddings)
    chunks = text_splitter.split_documents(documents)
    return chunks
```

### 4.2. Khối Nhúng & Lưu Cloud (Embedding & Cloud Vector DB)
Sử dụng **Pinecone** thay vì ChromaDB.
**File: `rag/retrieval/vectorstore.py`**
```python
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from core.config import settings
import os

# Set API Key cho Pinecone
os.environ["PINECONE_API_KEY"] = settings.PINECONE_API_KEY

def get_vectorstore():
    # Sử dụng mô hình nhúng BGE-M3 (Enterprise-grade)
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    # Trỏ đến Cloud Vector DB
    vectorstore = PineconeVectorStore(index_name=settings.PINECONE_INDEX_NAME, embedding=embeddings)
    return vectorstore

def add_documents_to_cloud_db(chunks):
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
```

**File: `rag/retrieval/search.py`**
```python
from rag.retrieval.vectorstore import get_vectorstore

def retrieve_relevant_chunks(query: str, k: int = 3):
    vectorstore = get_vectorstore()
    # Tìm kiếm với tốc độ dưới 10ms từ Cloud
    results = vectorstore.similarity_search(query, k=k)
    return results
```

---

## 5. Thư mục `services/` (Tầng Điều Phối - ETL Pipeline)

**File: `services/crawler_service.py`**
Đảm nhiệm chuỗi ETL: Extract (Web Scrape) -> Transform (Semantic Chunking) -> Load (Pinecone).
```python
from sqlalchemy.orm import Session
from db.models import CrawlRecord
from rag.ingestion.loaders import scrape_website
from rag.ingestion.chunkers import split_documents_semantically
from rag.retrieval.vectorstore import add_documents_to_cloud_db

async def process_url_crawl(url: str, db: Session):
    # --- Ghi Log Database Truyền Thống ---
    new_record = CrawlRecord(url=url, status="processing")
    db.add(new_record)
    db.commit()
    
    try:
        # 1. Extract: Cào dữ liệu từ Website (TTC AgriS)
        documents = scrape_website(url)
        
        # 2. Transform: Chia văn bản theo ngữ nghĩa
        chunks = split_documents_semantically(documents)
        
        # 3. Load: Đẩy lên Pinecone Cloud
        add_documents_to_cloud_db(chunks)
        
        # Cập nhật trạng thái thành công
        new_record.status = "success"
        db.commit()
        
        return f"Đã cào và lưu thành công {len(chunks)} đoạn ngữ nghĩa từ {url}"
    except Exception as e:
        new_record.status = "failed"
        db.commit()
        raise e
```

---

## 6. Hướng Dẫn Chạy Dự Án Enterprise

**Bổ sung thư viện vào `requirements.txt`:**
```text
beautifulsoup4 # Để cào dữ liệu Web
langchain-pinecone # Để kết nối Cloud Vector DB Pinecone
pinecone-client
langchain-experimental # Dành cho Semantic Chunker
```

**Tạo tài khoản Pinecone Miễn Phí (Serverless):**
1. Vào `pinecone.io`, đăng ký tài khoản.
2. Tạo một Index tên là `ttc-agris-reports`, chọn Dimension là `1024` (nếu dùng BGE-M3) hoặc `384` (nếu dùng MiniLM). Metric là `Cosine`.
3. Lấy API Key và lưu vào file `.env`:
   ```env
   GROQ_API_KEY=gsk_...
   PINECONE_API_KEY=pcsk_...
   ```

**Khởi chạy hệ thống bằng Docker/WSL:**
Gõ lệnh:
```bash
docker compose up -d --build
```
Truy cập `http://localhost:8000/docs`, vào API `/api/crawler` và thử cào link `https://ttcagris.com.vn/bao-cao-phat-trien-ben-vung`. Toàn bộ dữ liệu sẽ được bắn lên Cloud và sẵn sàng để Hỏi Đáp!
