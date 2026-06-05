from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from core.config import settings
from rag.retrieval.search import retrieve_relevant_chunks
from db.database import get_db
from db.models import ChatHistory

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    sessionId: str
    username: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []


class ChatSessionResponse(BaseModel):
    session_id: str
    title: str


class ChatHistoryResponse(BaseModel):
    user_message: str
    ai_response: str
    created_at: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Tìm kiếm ngữ cảnh trong Pinecone
    try:
        docs = retrieve_relevant_chunks(request.query)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Lấy danh sách nguồn (loại bỏ trùng lặp)
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in docs]))
    except Exception as e:
        print("Lỗi khi tìm kiếm vector db:", e)
        context = ""
        sources = []

    # 2. Xây dựng Prompt
    prompt_template = """
    Bạn là một trợ lý AI thông minh. Hãy trả lời câu hỏi của người dùng dựa trên NGỮ CẢNH được cung cấp.
    Nếu ngữ cảnh không có thông tin để trả lời, hãy nói rõ là bạn không tìm thấy thông tin.
    
    NGỮ CẢNH:
    {context}
    
    CÂU HỎI:
    {query}
    
    TRẢ LỜI:
    """
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "query"]
    )
    formatted_prompt = prompt.format(context=context, query=request.query)

    # 3. Gọi Groq LLM
    try:
        llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.1,
            api_key=settings.GROQ_API_KEY,
        )
        response = llm.invoke(formatted_prompt)
        answer = response.content
    except Exception as e:
        print("Lỗi khi gọi LLM:", e)
        answer = "Xin lỗi, đã có lỗi xảy ra khi gọi AI để sinh câu trả lời."

    # 4. Lưu lịch sử chat vào Database
    try:
        chat_record = ChatHistory(
            username=request.username,
            session_id=request.sessionId,
            user_message=request.query,
            ai_response=answer,
        )
        db.add(chat_record)
        db.commit()
    except Exception as e:
        print("Lỗi khi lưu lịch sử chat:", e)

    return ChatResponse(answer=answer, sources=sources)


@router.get("/sessions/{username}", response_model=List[ChatSessionResponse])
async def get_sessions(username: str, db: Session = Depends(get_db)):
    """Lấy danh sách các session chat của user, sắp xếp theo thời gian mới nhất."""
    # Lấy các session_id duy nhất của user, cùng thời điểm tạo mới nhất
    sessions = (
        db.query(
            ChatHistory.session_id,
            func.min(ChatHistory.user_message).label("first_message"),
            func.max(ChatHistory.created_at).label("latest"),
        )
        .filter(ChatHistory.username == username)
        .group_by(ChatHistory.session_id)
        .order_by(func.max(ChatHistory.created_at).desc())
        .all()
    )

    result = []
    for s in sessions:
        # Dùng tin nhắn đầu tiên làm tiêu đề, cắt ngắn nếu quá dài
        title = s.first_message or "Đoạn chat mới"
        if len(title) > 50:
            title = title[:50] + "..."
        result.append(
            ChatSessionResponse(session_id=s.session_id, title=title)
        )
    return result


@router.get("/history/{sessionId}", response_model=List[ChatHistoryResponse])
async def get_history(sessionId: str, db: Session = Depends(get_db)):
    """Lấy toàn bộ lịch sử chat của một session, sắp xếp theo thời gian."""
    records = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == sessionId)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )
    return [
        ChatHistoryResponse(
            user_message=r.user_message,
            ai_response=r.ai_response,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in records
    ]


@router.delete("/history/{sessionId}")
async def delete_history(sessionId: str, db: Session = Depends(get_db)):
    """Xóa toàn bộ lịch sử chat của một session."""
    deleted = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == sessionId)
        .delete()
    )
    db.commit()
    return {"message": f"Đã xóa {deleted} tin nhắn của session {sessionId}"}


@router.delete("/history/all/{username}")
async def delete_all_history(username: str, db: Session = Depends(get_db)):
    """Xóa toàn bộ lịch sử chat của một user."""
    deleted = (
        db.query(ChatHistory)
        .filter(ChatHistory.username == username)
        .delete()
    )
    db.commit()
    return {"message": f"Đã xóa {deleted} tin nhắn của user {username}"}
