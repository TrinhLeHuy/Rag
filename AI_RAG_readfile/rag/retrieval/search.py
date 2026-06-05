from rag.retrieval.vectorstore import get_vectorstore
from core.config import settings

def retrieve_relevant_chunks(query: str):
    vectorstore = get_vectorstore()
    # Sử dụng MMR (Maximal Marginal Relevance) để tối ưu hóa sự đa dạng của các tài liệu
    # Giúp lấy thông tin từ nhiều file khác nhau thay vì chỉ tập trung vào 1 file có điểm tương đồng cao nhất
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": settings.RETRIEVER_K}
    )
    return retriever.invoke(query)
