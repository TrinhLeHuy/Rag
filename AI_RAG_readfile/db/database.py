from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Lấy cấu hình kết nối từ settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Cấu hình engine kết nối. Với SQLite cần thêm check_same_thread=False
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

# Khởi tạo SessionLocal để tạo ra các session làm việc với CSDL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo Base class cho các model kế thừa
Base = declarative_base()

# Hàm lấy DB session (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
