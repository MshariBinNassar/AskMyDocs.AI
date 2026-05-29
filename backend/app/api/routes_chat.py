from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import ollama

from app.services.session_store import (
    get_session,
    add_message_to_session,
    rename_session
)

from app.services.embeddings import create_embedding
from app.services.vector_store import search_chunks


router = APIRouter(prefix="/sessions", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str

def generate_session_name(question: str) -> str:
    q = question.lower()

    if "certification" in q or "certifications" in q or "certs" in q:
        return "Cloud Certifications"

    if "cv" in q or "resume" in q:
        return "CV Review"

    if "experience" in q:
        return "Work Experience"

    if "skills" in q:
        return "Skills Summary"

    return "Document Q&A"

@router.post("/{session_id}/chat")
def chat_with_session(
    session_id: str,
    request: ChatRequest
):
    session = get_session(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.get("name") == "New Session":
        auto_name = generate_session_name(request.question)
        rename_session(session_id, auto_name)

    question_embedding = create_embedding(request.question)

    results = search_chunks(
        embedding=question_embedding,
        top_k=3,
        session_id=session_id
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "answer": "No relevant context found in this session.",
            "sources": []
        }

    context = "\n\n---\n\n".join(documents)

    add_message_to_session(
    session_id=session_id,
    role="user",
    content=request.question
    )

    response = ollama.chat(
        model="krith/qwen2.5-7b-instruct:IQ4_XS",
        messages=[
            {
                "role": "system",
                "content": f"""
You are AskMyDocs.AI, a local document assistant.

Answer the user's question using ONLY the context below.
If the answer is not found in the context, say:
"I could not find this information in the uploaded documents."

Context:
{context}
"""
            },
            {
                "role": "user",
                "content": request.question
            }
        ]
    )

    sources = []

    for index, metadata in enumerate(metadatas):
        sources.append({
        "filename": metadata.get("filename", "Unknown file"),
        "chunk_index": metadata.get("chunk_index", 0),
        "preview": documents[index]
    })

    add_message_to_session(
        session_id=session_id,
        role="assistant",
        content=response["message"]["content"],
        sources=sources
    )

    return {
        "answer": response["message"]["content"],
        "sources": sources
    }