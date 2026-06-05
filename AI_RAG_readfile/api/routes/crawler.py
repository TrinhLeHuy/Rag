from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from services.crawler_service import process_url_crawl_background
from db.database import get_db
from db.models import CrawlRecord

router = APIRouter()


class CrawlRequest(BaseModel):
    url: str = "https://ttcagris.com.vn/bao-cao-phat-trien-ben-vung"


@router.post("/", status_code=202)
async def start_crawl(
    req: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Nhận URL, tạo job record ngay lập tức, rồi chạy xử lý trong background.
    Trả về job_id để frontend dùng để poll tiến độ — KHÔNG chờ xử lý xong.
    """
    # Tạo record trong DB với trạng thái "queued"
    new_record = CrawlRecord(
        url=req.url,
        status="queued",
        message="⏳ Đã nhận yêu cầu, đang chờ xử lý...",
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    # Đẩy vào hàng đợi background — không block response
    background_tasks.add_task(process_url_crawl_background, req.url, new_record.id)

    return {
        "job_id": new_record.id,
        "status": "queued",
        "message": "Đã nhận yêu cầu! Dùng job_id để kiểm tra tiến độ.",
    }


@router.get("/{job_id}")
async def get_crawl_status(job_id: int, db: Session = Depends(get_db)):
    """Frontend poll endpoint này mỗi vài giây để lấy trạng thái job."""
    record = db.query(CrawlRecord).filter(CrawlRecord.id == job_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy job #{job_id}")

    return {
        "job_id": record.id,
        "url": record.url,
        "status": record.status,   # queued | processing | success | failed
        "message": record.message or "",
    }
