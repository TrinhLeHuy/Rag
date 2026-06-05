from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_core.documents import Document
import pytesseract
from PIL import Image
import os
import base64
import requests
import io
from core.config import settings

def analyze_image_with_groq(image_path_or_pil):
    """
    Sử dụng model Llama 4 Scout (Vision) của Groq để đọc ảnh và biểu đồ.
    Nếu thất bại sẽ dùng Tesseract OCR làm phương án dự phòng.
    """
    try:
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("No Groq API Key found")

        # Chuyển ảnh sang Base64
        if isinstance(image_path_or_pil, str):
            with open(image_path_or_pil, 'rb') as f:
                base64_image = base64.b64encode(f.read()).decode('utf-8')
        else:
            buffered = io.BytesIO()
            # Convert to RGB to avoid issues with saving as JPEG/PNG if it has alpha
            img_rgb = image_path_or_pil.convert('RGB')
            img_rgb.save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct", # Model Vision mới nhất của Groq
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Hãy phân tích chi tiết biểu đồ hoặc hình ảnh này. Hãy trích xuất toàn bộ chữ viết (text), các số liệu trong bảng biểu, và mô tả xu hướng chính nếu là biểu đồ. Trả về dưới dạng văn bản chi tiết."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1024
        }
        
        import time
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            
            error_data = response.json()
            if response.status_code == 429 or (error_data.get('error') and error_data['error'].get('code') == 'rate_limit_exceeded'):
                print(f"Bị giới hạn tốc độ Groq API (Rate limit). Đang đợi 6 giây trước khi thử lại (lần {attempt+1}/{max_retries})...")
                time.sleep(6)
            else:
                print("Groq Vision Error:", error_data)
                break
            
    except Exception as e:
        print(f"Error using Groq Vision API: {e}")
        
    # Phương án dự phòng: Dùng Tesseract truyền thống
    try:
        if isinstance(image_path_or_pil, str):
            with Image.open(image_path_or_pil) as img:
                return pytesseract.image_to_string(img)
        else:
            return pytesseract.image_to_string(image_path_or_pil)
    except:
        return ""

def load_document(file_path: str):
    file_ext = file_path.lower()
    
    if file_ext.endswith((".png", ".jpg", ".jpeg")):
        # Thực hiện đọc ảnh/biểu đồ bằng Groq
        text = analyze_image_with_groq(file_path)
        return [Document(page_content=text, metadata={"source": file_path, "type": "image_analysis"})]
        
    elif file_ext.endswith(".pdf"):
        from pypdf import PdfReader
        import pdfplumber
        import io
        from PIL import Image
        
        docs = []
        
        with pdfplumber.open(file_path) as pdf_plumb:
            reader = PdfReader(file_path)
            
            for i, page_pypdf in enumerate(reader.pages):
                page_plumb = pdf_plumb.pages[i]
                
                # 1. Trích xuất chữ (text) và Bảng (table) bằng pdfplumber
                text = page_plumb.extract_text() or ""
                
                tables = page_plumb.extract_tables()
                if tables:
                    table_texts = []
                    for table in tables:
                        table_str = ""
                        for row_index, row in enumerate(table):
                            clean_row = [str(cell).replace('\n', ' ') if cell is not None else "" for cell in row]
                            table_str += "| " + " | ".join(clean_row) + " |\n"
                            if row_index == 0:
                                table_str += "|" + "|".join(["---" for _ in clean_row]) + "|\n"
                        table_texts.append(f"\n[Bảng dữ liệu]:\n{table_str}\n")
                    text += "\n" + "\n".join(table_texts)
                
                # 2. Trích xuất hình ảnh có trong trang bằng pypdf
                image_analyses = []
                for image_file_object in page_pypdf.images:
                    try:
                        img = Image.open(io.BytesIO(image_file_object.data))
                        # Đưa qua Groq để đọc ảnh/biểu đồ
                        img_analysis = analyze_image_with_groq(img)
                        if img_analysis:
                            image_analyses.append(f"[Hình ảnh/Biểu đồ: {img_analysis}]")
                    except Exception as e:
                        print(f"Lỗi khi trích xuất ảnh ở trang {i}: {e}")
                
                # Nối phần mô tả ảnh vào nội dung trang
                if image_analyses:
                    if text.strip():
                        text += "\n\n"
                    text += "\n\n".join(image_analyses)
                    
                # 3. Dự phòng (Fallback): Nếu trang trống trơn
                if not text.strip():
                    try:
                        from pdf2image import convert_from_path
                        pages = convert_from_path(file_path, first_page=i+1, last_page=i+1)
                        if pages:
                            text = analyze_image_with_groq(pages[0])
                    except Exception as e:
                        print(f"Lỗi khi fallback pdf2image ở trang {i}: {e}")
                        
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"source": file_path, "page": i, "type": "pdf"}))
                    
        return docs
        
    elif file_ext.endswith(".docx"):
        import docx2txt
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            text = docx2txt.process(file_path, tmpdir)
            if not text:
                text = ""
                
            for img_file in os.listdir(tmpdir):
                if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(tmpdir, img_file)
                    try:
                        # Phân tích ảnh/biểu đồ đính kèm trong Word
                        img_text = analyze_image_with_groq(img_path)
                        if text:
                            text += f"\n[Hình ảnh/Biểu đồ: {img_text}]\n"
                        else:
                            text = img_text
                    except Exception:
                        pass
        
        return [Document(page_content=text, metadata={"source": file_path, "type": "docx"})]
    else:
        loader = TextLoader(file_path, encoding="utf-8")
        return loader.load()

from langchain_community.document_loaders import WebBaseLoader
import bs4
import tempfile

def scrape_website(url: str):
    if url.lower().endswith(".pdf"):
        # Tải file PDF tạm thời về máy
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
            
        try:
            # Dùng lại hàm load_document đã có để bóc tách cả text và hình ảnh
            docs = load_document(tmp_file_path)
            # Cập nhật metadata source thành URL gốc thay vì đường dẫn file tạm
            for doc in docs:
                doc.metadata["source"] = url
            return docs
        finally:
            # Xóa file tạm sau khi đã xử lý xong
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
    else:
        loader = WebBaseLoader(
            web_paths=(url,),
            requests_kwargs={'timeout': 120}
        )
        docs = loader.load()
        return docs

