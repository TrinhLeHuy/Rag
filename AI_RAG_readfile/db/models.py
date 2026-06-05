from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from db.database import Base

# Bảng 1: Lưu trữ thông tin Crawler
class CrawlRecord(Base):
    __tablename__ = "crawl_records"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True) 
    start_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="queued")  # queued, processing, success, failed
    message = Column(Text, default="")         # Thông tin tiến độ chi tiết

# Bảng 2: Lưu lịch sử chat
class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True) # Tên người dùng sở hữu đoạn chat này
    session_id = Column(String, index=True) # Mã phiên chat (để phân biệt các cuộc hội thoại khác nhau)
    user_message = Column(Text) # Câu hỏi của người dùng (Text chứa được chuỗi rất dài)
    ai_response = Column(Text) # Câu trả lời của AI
    created_at = Column(DateTime, default=datetime.utcnow)

# Bảng 3: Lưu thông tin người dùng (Đăng ký / Đăng nhập)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String) # Thực tế cần mã hóa mật khẩu (hash), đây là bản đơn giản cho người mới
