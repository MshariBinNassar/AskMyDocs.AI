const API_BASE_URL = "http://127.0.0.1:8000";

export async function createSession(name) {
    const response = await fetch(
        `${API_BASE_URL}/sessions/`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name
            })
        }
    );

    return response.json();
}

export async function getSessions() {
    const response = await fetch(
        `${API_BASE_URL}/sessions/`
    );

    return response.json();
}

export async function getSession(sessionId) {
    const response = await fetch(
        `${API_BASE_URL}/sessions/${sessionId}`
    );

    return response.json();
}