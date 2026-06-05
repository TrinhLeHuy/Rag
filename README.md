# 📚 Dự án RAG Đa Dụng (AI Retrieval-Augmented Generation)

Một hệ thống ứng dụng RAG (Retrieval-Augmented Generation) toàn diện, kết hợp sức mạnh xử lý của backend **Python (FastAPI)** và giao diện tương tác mượt mà của frontend **Blazor WebAssembly (.NET)**.

Dự án cho phép người dùng tải lên và thu thập thông tin từ nhiều nguồn tài liệu khác nhau, trích xuất dữ liệu, lưu trữ dưới dạng vector embeddings, và trò chuyện trực tiếp với tài liệu dựa trên mô hình ngôn ngữ từ **Groq** (Llama / Groq API).

---

## ✨ Tính năng nổi bật

- **Đa dạng định dạng tài liệu**: Hỗ trợ xử lý PDF, DOCX, ảnh (thông qua Groq Vision hoặc fallback Tesseract) và thu thập thông tin từ trang web.
- **Xử lý ngôn ngữ tự nhiên thông minh**: Phân chia văn bản (chunking) thông minh và lưu trữ embeddings vào vector database (tích hợp Pinecone và ChromaDB).
- **Tương tác thời gian thực (Chat RAG)**: API cung cấp câu trả lời chính xác, kèm theo trích dẫn nguồn (ngữ cảnh) trực tiếp từ tài liệu đã nạp.
- **Xử lý nền mạnh mẽ (Background Jobs)**: Cơ chế thu thập dữ liệu bất đồng bộ (Crawler) không gây nghẽn hệ thống, dễ dàng theo dõi tiến độ công việc.
- **Quản lý phiên hội thoại**: Lưu trữ lịch sử trò chuyện và quản lý session người dùng bằng SQLite.

---

## 🏗️ Kiến trúc Hệ thống

Hệ thống được chia làm hai phần chính hoạt động độc lập:

### 1. Backend: `AI_RAG_readfile/` (Python / FastAPI)
Đảm nhiệm vai trò lõi xử lý dữ liệu RAG, trích xuất nội dung, vector hóa và giao tiếp với LLM.
- **Framework**: FastAPI
- **Tính năng**: APIs, RAG Logic, Vector Database Integration, Background tasks.

### 2. Frontend: `RagFrontend/` (Blazor WebAssembly)
Giao diện người dùng dạng Single Page Application (SPA), tương tác mượt mà thông qua việc gọi các RESTful APIs từ backend.
- **Framework**: .NET 9 Blazor WASM
- **Tính năng**: Quản lý hội thoại, hiển thị trạng thái xử lý tài liệu, tải lên file.

---

## 🚀 Hướng dẫn Cài đặt & Khởi chạy

### Yêu cầu hệ thống
- **.NET 9 SDK** (dành cho môi trường frontend).
- **Python 3.10+** (dành cho môi trường backend).
- Các công cụ hỗ trợ đọc ảnh OCR: cài đặt **Tesseract** (trong trường hợp không sử dụng Groq Vision).

### BƯỚC 1: Cài đặt và Chạy Backend (FastAPI)

1. Mở terminal, truy cập vào thư mục chứa backend và khởi tạo môi trường ảo:
   ```powershell
   cd AI_RAG_readfile
   python -m venv .venv
   .\.venv\Scripts\activate  # Với Windows
   # source .venv/bin/activate # Với Linux/MacOS
   ```

2. Cài đặt các thư viện cần thiết:
   ```powershell
   pip install -r requirements.txt
   ```

3. Cấu hình biến môi trường: 
   Tạo file `.env` tại thư mục gốc của backend (`AI_RAG_readfile/`) và cấu hình theo mẫu sau:
   ```env
   GROQ_API_KEY=your_groq_api_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_INDEX_NAME=your_index_name
   DATABASE_URL=sqlite:///./rag_database_v2.db
   ```

4. Chạy server phát triển:
   ```powershell
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```
   > 💡 Backend sẽ chạy tại: `http://localhost:8000`. Bạn có thể truy cập `http://localhost:8000/docs` để xem tài liệu Swagger API chi tiết.

### BƯỚC 2: Cài đặt và Chạy Frontend (Blazor)

1. Mở một terminal mới, truy cập vào thư mục frontend:
   ```powershell
   cd RagFrontend
   ```

2. Chạy ứng dụng Blazor:
   ```powershell
   dotnet run
   ```
   > 💡 Frontend sẽ chạy tại `https://localhost:5001` (hoặc `http://localhost:5000`). Giao diện sẽ tự động cấu hình gọi API tới backend tại cổng 8000.

---

## 🔌 Danh sách API Chính

| Phương thức | Endpoint | Mô tả |
| :--- | :--- | :--- |
| **POST** | `/api/chat/` | Đặt câu hỏi RAG (Payload: `query`, `sessionId`, `username`). Trả về câu trả lời kèm context. |
| **GET** | `/api/chat/sessions/{username}` | Lấy danh sách các phiên trò chuyện của người dùng hiện tại. |
| **GET** | `/api/chat/history/{sessionId}` | Truy xuất chi tiết lịch sử tin nhắn trong một phiên. |
| **POST** | `/api/crawler/` | Kích hoạt job crawl để thu thập & xử lý tài liệu nền (trả về `job_id`). |
| **GET** | `/api/crawler/{job_id}` | Lấy trạng thái xử lý tiến độ của job tương ứng. |

---

## 📁 Cấu trúc Thư mục Tổng quan

```text
📦 web_rag
 ┣ 📂 AI_RAG_readfile          # (Backend - Python FastAPI)
 ┃ ┣ 📂 api                    # API endpoints và định tuyến ứng dụng
 ┃ ┣ 📂 core                   # Cấu hình chung, thiết lập logging & biến môi trường
 ┃ ┣ 📂 db                     # Database ORM models (SQLAlchemy)
 ┃ ┣ 📂 rag                    # Logic cốt lõi: Ingestion (Loaders, Chunking) và Retrieval
 ┃ ┣ 📜 requirements.txt       # Các thư viện phụ thuộc Python
 ┃ ┗ 📜 .env                   # File chứa biến môi trường (người dùng tự tạo)
 ┗ 📂 RagFrontend              # (Frontend - .NET 9 Blazor WASM)
   ┣ 📂 Pages                  # Các components giao diện (Chat, Upload, v.v.)
   ┣ 📂 Services               # Các service kết nối HTTP tới backend (VD: ChatService)
   ┗ 📜 Program.cs             # Điểm cấu hình và khởi chạy ứng dụng Blazor
```

---

## ⚠️ Lưu ý Quan trọng khi Triển khai (Deployment)

1. **Bảo mật Hệ thống**: 
   - Mã nguồn hiện tại lưu mật khẩu thô trong SQLite với mục đích demo/học tập. Hãy cập nhật thuật toán băm (hashing như `bcrypt`) và áp dụng tiêu chuẩn bảo mật xác thực tiên tiến trước khi đưa lên production.
2. **Quản lý Khóa API (API Keys)**:
   - Hãy chắc chắn biến `GROQ_API_KEY` hợp lệ để bộ não LLM của ứng dụng hoạt động trơn tru.
   - Cần đảm bảo index name trên Pinecone hoàn toàn khớp với `PINECONE_INDEX_NAME`.
3. **Cơ sở dữ liệu Production**:
   - Đối với môi trường sản xuất thực tế có nhiều lượt truy cập, SQLite nên được nâng cấp thành **PostgreSQL** hoặc **MySQL**.
4. **Rate Limit từ Bên thứ Ba**:
   - Lượt gọi tới API của Groq và Pinecone có thể gặp hạn chế theo mức gói đăng ký. Hệ thống đã tích hợp sẵn cơ chế retry nhẹ, nhưng cần theo dõi kỹ log trong môi trường có lưu lượng xử lý tài liệu lớn.

---

## 🛠️ Lộ trình Phát triển (Roadmap) & Đóng góp

- [ ] **Dockerization**: Đóng gói backend/frontend bằng Docker để giúp triển khai 1-chạm (one-click deployment).
- [ ] **Bảo mật & Phân quyền**: Cải tiến luồng xác thực, thêm Role-based Access Control (RBAC).
- [ ] **Kiểm thử tự động**: Viết bổ sung Unit Tests cho backend và tích hợp vào quy trình CI/CD.

**🤝 Đóng góp:** Cộng đồng luôn được chào đón! Bạn có thể fork dự án này, tạo một nhánh (`branch`) mới với những thay đổi ấn tượng, test kĩ càng rồi gửi Pull Request (PR) về repository. Hãy mô tả chi tiết logic sửa đổi của bạn nhé!
