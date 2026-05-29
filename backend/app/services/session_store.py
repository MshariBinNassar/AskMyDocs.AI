from pathlib import Path
from uuid import uuid4
from datetime import datetime
import json

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)


def create_session(name: str | None = None):
    session_id = str(uuid4())

    session_data = {
    "session_id": session_id,
    "name": name or "New Session",
    "created_at": datetime.utcnow().isoformat(),
    "files": [],
    "messages": []
}

    session_file = SESSIONS_DIR / f"{session_id}.json"

    with session_file.open("w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

    return session_data


def get_session(session_id: str):
    session_file = SESSIONS_DIR / f"{session_id}.json"

    if not session_file.exists():
        return None

    with session_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_session(session_data: dict):
    session_data["updated_at"] = datetime.utcnow().isoformat()

    session_file = SESSIONS_DIR / f"{session_data['session_id']}.json"

    with session_file.open("w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)


def add_file_to_session(session_id: str, file_data: dict):
    session_data = get_session(session_id)

    if session_data is None:
        return None

    session_data["files"].append(file_data)
    save_session(session_data)

    return session_data

def list_sessions():
    sessions = []

    for file in SESSIONS_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            session = json.load(f)
            sessions.append(session)

    sessions.sort(
        key=lambda session: session.get("updated_at", session.get("created_at", "")),
        reverse=True
    )

    return sessions

def add_message_to_session(
    session_id: str,
    role: str,
    content: str,
    sources: list | None = None
):
    session_data = get_session(session_id)

    if session_data is None:
        return None

    if "messages" not in session_data:
        session_data["messages"] = []

    message = {
        "role": role,
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
        "sources": sources or []
    }

    session_data["messages"].append(message)

    save_session(session_data)

    return message

def rename_session(session_id: str, name: str):
    session_data = get_session(session_id)

    if session_data is None:
        return None

    session_data["name"] = name
    save_session(session_data)

    return session_data

def delete_session(session_id: str):
    session_file = SESSIONS_DIR / f"{session_id}.json"

    if not session_file.exists():
        return False

    session_file.unlink()
    return True

