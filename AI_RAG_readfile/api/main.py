from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, crawler, auth
from core.config import settings
from db.database import engine, Base
import os

# Remove upload dir creation since we don't need it

# Tự động tạo các Bảng trong Database (nếu chưa có)
Base.metadata.create_all(bind=engine)

# Khởi tạo phần mềm FastAPI (một web framework rất nhanh của Python)
app = FastAPI(title=settings.PROJECT_NAME)

# Cấu hình CORS (Cross-Origin Resource Sharing - Chia sẻ tài nguyên chéo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép MỌI trang web được quyền gọi API này
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nhúng (include) các đường dẫn (routes)
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(crawler.router, prefix="/api/crawler", tags=["Web Crawler"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
