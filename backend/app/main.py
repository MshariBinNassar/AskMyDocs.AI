from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_upload import router as upload_router
from app.api.routes_sessions import router as sessions_router
from app.api.routes_chat import router as chat_router

app = FastAPI(
    title="AskMyDocs.AI API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(sessions_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "AskMyDocs.AI backend is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}