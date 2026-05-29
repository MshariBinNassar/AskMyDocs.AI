from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path
from uuid import uuid4
import shutil

from app.services.session_store import (
    create_session,
    get_session,
    add_file_to_session,
    list_sessions,
    rename_session,
    delete_session
)

from app.services.document_loader import extract_pdf_text
from app.services.chunking import chunk_text
from app.services.embeddings import create_embedding
from app.services.vector_store import store_chunk


router = APIRouter(prefix="/sessions", tags=["Sessions"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class CreateSessionRequest(BaseModel):
    name: str | None = None


@router.post("/")
def create_new_session(request: CreateSessionRequest):
    return create_session(request.name)


@router.post("/{session_id}/upload")
def upload_file_to_session(
    session_id: str,
    file: UploadFile = File(...)
):
    session = get_session(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    file_id = str(uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_pdf_text(str(file_path))
    chunks = chunk_text(text)

    for index, chunk in enumerate(chunks):
        embedding = create_embedding(chunk)

        chunk_id = f"{session_id}_{file_id}_chunk_{index}"

        store_chunk(
            chunk_id=chunk_id,
            text=chunk,
            embedding=embedding,
            metadata={
                "session_id": session_id,
                "file_id": file_id,
                "filename": file.filename,
                "chunk_index": index
            }
        )

    file_data = {
        "file_id": file_id,
        "filename": file.filename,
        "path": str(file_path),
        "chunks_count": len(chunks),
        "status": "indexed"
    }

    updated_session = add_file_to_session(session_id, file_data)

    return {
        "message": "File uploaded and indexed successfully",
        "session": updated_session
    }

@router.get("/")
def get_sessions():
    return list_sessions()

@router.get("/{session_id}")
def get_session_details(session_id: str):

    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session

class RenameSessionRequest(BaseModel):
    name: str


@router.patch("/{session_id}")
def rename_existing_session(
    session_id: str,
    request: RenameSessionRequest
):
    session = rename_session(session_id, request.name)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session

@router.delete("/{session_id}")
def delete_existing_session(session_id: str):
    deleted = delete_session(session_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return {
        "message": "Session deleted successfully"
    }