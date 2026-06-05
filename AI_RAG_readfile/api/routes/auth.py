from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User

router = APIRouter()


class AuthRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(req: AuthRequest, db: Session = Depends(get_db)):
    """Đăng ký tài khoản mới. Trả 400 nếu username đã tồn tại."""
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username đã tồn tại")

    new_user = User(username=req.username, password=req.password)
    db.add(new_user)
    db.commit()
    return {"message": "Đăng ký thành công!", "username": req.username}


@router.post("/login")
async def login(req: AuthRequest, db: Session = Depends(get_db)):
    """Đăng nhập. Trả 401 nếu sai tên hoặc mật khẩu."""
    user = (
        db.query(User)
        .filter(User.username == req.username, User.password == req.password)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu"
        )
    return {"message": "Đăng nhập thành công!", "username": user.username}
