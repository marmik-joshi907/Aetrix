"""
Chat API Route.

POST /api/chat — RAG-powered chatbot endpoint.
Accepts a user message with optional city/week context,
returns an AI-generated reply with source references.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    city: Optional[str] = "Ahmedabad"
    week: Optional[int] = -1


class ChatResponse(BaseModel):
    reply: str
    sources: list


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Answer a user question using the RAG engine."""
    from rag.rag_engine import get_engine

    engine = get_engine()
    if engine is None:
        raise HTTPException(
            status_code=503,
            detail="Chat engine not initialized. Please try again later.",
        )

    result = engine.ask(
        question=req.message,
        city=req.city or "Ahmedabad",
        week=req.week if req.week is not None else -1,
    )

    return ChatResponse(
        reply=result["reply"],
        sources=result.get("sources", []),
    )
