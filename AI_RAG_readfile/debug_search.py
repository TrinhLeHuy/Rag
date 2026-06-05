import os
import sys
from core.config import settings
from rag.retrieval.search import retrieve_relevant_chunks

def debug_query(query: str):
    print(f"\n--- THỰC HIỆN TÌM KIẾM CHO CÂU HỎI: '{query}' ---")
    try:
        docs = retrieve_relevant_chunks(query)
        if not docs:
            print("Không tìm thấy chunk nào!")
            return
            
        for i, doc in enumerate(docs):
            print(f"\n[Chunk {i+1}] (Nguồn: {doc.metadata.get('source', 'Unknown')} - Page: {doc.metadata.get('page', 'Unknown')} - Loại: {doc.metadata.get('type', 'Unknown')})")
            content = doc.page_content
            # Cắt ngắn nếu quá dài
            if len(content) > 500:
                print(content[:500] + "...\n[...còn tiếp...]")
            else:
                print(content)
            print("-" * 50)
            
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    queries = [
        "Quy trình kiểm soát chất lượng sản phẩm",
        "Quá trình kiểm soát ATLĐ & sức khoẻ ở AgriS"
    ]
    for q in queries:
        debug_query(q)
