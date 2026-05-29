import chromadb

client = chromadb.PersistentClient(path="vector_db")

collection = client.get_or_create_collection(name="documents")


def store_chunk(
    chunk_id: str,
    text: str,
    embedding: list,
    metadata: dict | None = None
):
    collection.add(
        ids=[chunk_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata or {}]
    )


def count_chunks():
    return collection.count()


def search_chunks(
    embedding: list,
    top_k: int = 3,
    session_id: str | None = None
):
    where_filter = {"session_id": session_id} if session_id else None

    return collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where_filter,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )