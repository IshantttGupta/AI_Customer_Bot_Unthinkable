

# backend/app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from rag_model import create_session, post_message, get_history  # import functions from your model

app = FastAPI()

# =========================
# CORS Middleware
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for dev; restrict later in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Create a new session (user)
# =========================
@app.post("/create_session")
async def create_new_session():
    """Creates a new user session."""
    session = create_session()
    return session


# =========================
# Send user query and get model response
# =========================
@app.post("/chat")
async def chat(request: Request):
    """Handle user query and return bot reply + confidence."""
    data = await request.json()
    query = data.get("query", "")
    session_id = data.get("session_id")

    # Create session if not provided
    if not session_id:
        session = create_session()
        session_id = session["sessionId"]

    # Call your RAG pipeline
    try:
        response = post_message(session_id, query)

        return {
            "reply": response["reply"],
            "status": response["status"],
            "confidence": response["confidence"],
            "session_id": session_id,  # return for frontend tracking
        }

    except Exception as e:
        return {
            "reply": f"⚠️ Error: {str(e)}",
            "status": "error",
            "confidence": 0.0,
            "session_id": session_id,
        }


# =========================
# Get chat history
# =========================
@app.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Retrieve full chat history for a given session."""
    return get_history(session_id)

