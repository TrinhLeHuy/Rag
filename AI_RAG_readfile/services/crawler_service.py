from db.models import CrawlRecord
from db.database import SessionLocal
from rag.ingestion.loaders import scrape_website
from rag.ingestion.chunkers import split_documents_semantically
from rag.retrieval.vectorstore import add_documents_to_cloud_db


def update_job_status(job_id: int, status: str, message: str):
    db = SessionLocal()
    try:
        record = db.query(CrawlRecord).filter(CrawlRecord.id == job_id).first()
        if record:
            record.status = status
            record.message = message
            db.commit()
    except Exception as e:
        print(f"Error updating job status: {e}")
    finally:
        db.close()


def process_url_crawl_background(url: str, job_id: int):
    """
    Chạy trong background (BackgroundTasks của FastAPI).
    Cập nhật trạng thái từng bước để frontend có thể poll.
    Không giữ kết nối DB trong lúc đang crawl để tránh kẹt DB pool.
    """
    try:
        # --- Bước 1: Đánh dấu đang xử lý ---
        update_job_status(job_id, "processing", "🌐 Đang tải nội dung từ URL...")

        # --- Bước 2: Scrape / tải tài liệu ---
        documents = scrape_website(url)
        page_count = len(documents)

        update_job_status(job_id, "processing", f"📄 Đã tải xong {page_count} trang. Đang phân tích ngữ nghĩa (Semantic Chunking)...")

        # --- Bước 3: Chia chunk ngữ nghĩa ---
        chunks = split_documents_semantically(documents)

        update_job_status(job_id, "processing", f"🧩 Đã tạo {len(chunks)} đoạn. Đang lưu lên Pinecone Cloud DB...")

        # --- Bước 4: Đẩy lên Pinecone ---
        add_documents_to_cloud_db(chunks)

        # --- Hoàn tất ---
        update_job_status(job_id, "success", f"✅ Hoàn tất! Đã lưu {len(chunks)} đoạn ngữ nghĩa từ {url}")

    except Exception as e:
        # Ghi lỗi vào DB để frontend biết
        update_job_status(job_id, "failed", f"❌ Lỗi: {str(e)}")

