# # Customer Support Bot (RAG + Memory + Escalation) using Gemini, PyPDFLoader, FAISS
# # Aligns with the attached spec: FAQs/KB input, contextual memory, escalation, REST-like API [attached_file:122]
# # pip install -U langchain langchain-community langchain-google-genai faiss-cpu pypdf python-dotenv

# import os
# import time
# import uuid
# from typing import Dict, List, Optional, Tuple

# #me
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain_community.document_loaders import PyPDFLoader


# # --- Gemini via LangChain ---
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# # --- PDF loading and chunking ---
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter

# # --- Vector store (FAISS) ---
# from langchain_community.vectorstores import FAISS

# # --- Prompt + message types ---
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.schema import HumanMessage, AIMessage

# # =========================
# # Configuration (set once)
# # =========================

# API_KEY = "AIzaSyD3cklQJQxVJl9DOtonk7aXTDh8Y651mz0"  # For local testing only; rotate and do not commit
# CHAT_MODEL = "gemini-2.5-flash"                      # swap to "gemini-1.5-pro" for higher quality
# EMBED_MODEL = "models/text-embedding-004"           # Gemini embeddings model id
# CHUNK_SIZE = 900
# CHUNK_OVERLAP = 150
# TOP_K = 5
# MAX_TURNS = 10                                       # rolling memory window
# CONF_LOW_LEN = 25                                    # heuristic: short answers are less confident
# CONF_NO_HIT_PENALTY = 0.25                           # penalty if retrieval returns no docs
# ESCALATE_THRESHOLD = 0.45                            # tune for demos

# # =========================
# # Load Knowledge Base (PDF)
# # =========================
# # Use the attached spec PDF as the “FAQ/KB” for this demo, per Scope of Work [attached_file:122]
# PDF_PATH = r"C:\Users\Ishant Gupta\Downloads\kome-text.pdf"  # place the attached file in working dir

# loader = PyPDFLoader(PDF_PATH)                # parses pages into Documents [attached_file:122]
# pages = loader.load()

# splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
# chunks = splitter.split_documents(pages)

# emb = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=API_KEY)
# vectordb = FAISS.from_documents(chunks, emb)
# retriever = vectordb.as_retriever(search_kwargs={"k": TOP_K})

# # =========================
# # Session store (in-memory)
# # =========================
# # Mirrors “Database for session tracking” requirement; swap to Postgres/Mongo later [attached_file:122]
# Session = Dict[str, any]
# Message = Dict[str, str]

# SESSIONS: Dict[str, Session] = {}

# def _now() -> float:
#     return time.time()

# def create_session(user_id: Optional[str] = None) -> Dict:
#     sid = str(uuid.uuid4())
#     SESSIONS[sid] = {
#         "id": sid,
#         "user_id": user_id or "demo-user",
#         "status": "active",  # active|escalated|closed
#         "history": [],       # list[HumanMessage|AIMessage]
#         "created_at": _now(),
#         "escalations": []    # list of {reason, at}
#     }
#     return {"sessionId": sid, "status": "active"}

# def get_history(session_id: str) -> Dict:
#     s = SESSIONS[session_id]
#     # return plain text transcript for demo [attached_file:122]
#     transcript: List[Message] = []
#     for m in s["history"]:
#         role = "user" if isinstance(m, HumanMessage) else "assistant"
#         transcript.append({"role": role, "content": m.content})
#     return {"messages": transcript}

# def escalate_session(session_id: str, reason: str = "Low confidence"):
#     s = SESSIONS[session_id]
#     s["status"] = "escalated"
#     s["escalations"].append({"reason": reason, "at": _now()})
#     return {"status": "escalated", "ticketId": f"TKT-{session_id[:8]}".upper()}

# # =========================
# # Prompting and LLM client
# # =========================
# SYSTEM = """You are a helpful customer support assistant.
# Use the provided context snippets from the company spec/FAQ when relevant.
# If information is missing, ask one brief clarifying question or suggest the next actionable step.
# When using a context snippet, cite its index like.
# Prefer concise, friendly answers with clear next actions when appropriate."""

# prompt = ChatPromptTemplate.from_messages([
#     ("system", SYSTEM),
#     MessagesPlaceholder("history"),
#     ("human", "User query: {question}\n\nContext:\n{context}\n\nAnswer:")
# ])

# llm = ChatGoogleGenerativeAI(
#     model=CHAT_MODEL,
#     temperature=0.0,
#     convert_system_message_to_human=True,
#     google_api_key=API_KEY,
# )

# def _format_context(docs) -> str:
#     lines = []
#     for i, d in enumerate(docs, start=1):
#         text = d.page_content
#         if len(text) > 900:
#             text = text[:900] + "..."
#         lines.append(f"[{i}] {text}")
#     return "\n".join(lines)

# def _windowed(history: List, max_turns: int):
#     return history[-max_turns:]

# def _confidence(answer: str, hits: int) -> float:
#     # Simple heuristic suited for demo and “escalation simulation” in the spec [attached_file:122]
#     base = 0.7
#     if len(answer.strip()) < CONF_LOW_LEN:
#         base -= 0.3
#     if hits == 0:
#         base -= CONF_NO_HIT_PENALTY
#     base = max(0.0, min(1.0, base))
#     return base

# # =========================
# # REST-like message handler
# # =========================
# def post_message(session_id: str, content: str) -> Dict:
#     s = SESSIONS[session_id]
#     # 1) Retrieve
#     docs = retriever.invoke(content)
#     ctx = _format_context(docs)

#     # 2) Build messages with rolling memory
#     history = _windowed(s["history"], MAX_TURNS)
#     messages = prompt.format_messages(history=history, question=content, context=ctx)

#     # 3) LLM answer
#     ai = llm.invoke(messages)
#     answer = ai.content or ""

#     # 4) Confidence + possible escalation
#     conf = _confidence(answer, hits=len(docs))
#     status = s["status"]
#     cited_ids = list(range(1, len(docs) + 1))

#     # 5) Persist turn
#     s["history"].append(HumanMessage(content=content))
#     s["history"].append(AIMessage(content=answer))

#     # 6) Escalate if needed (simulation path per spec) [attached_file:122]
#     if conf < ESCALATE_THRESHOLD and status == "active":
#         s["status"] = "escalated"
#         s["escalations"].append({"reason": "Low confidence", "at": _now()})
#         status = "escalated"
#         # Append escalation notice to answer for UX
#         answer = answer + "\n\nIt looks like this needs review by a support agent. A ticket has been opened."

#     return {
#         "reply": answer,
#         "citedFaqIds": cited_ids,  # indices in the current retrieval batch
#         "status": status,
#         "confidence": round(conf, 2),
#     }

# # =========================
# # Demo run (CLI)
# # =========================
# if __name__ == "__main__":
#     sess = create_session()
#     sid = sess["sessionId"]
#     print("Session:", sid, "- status:", sess["status"])
#     print("Type 'history' to see transcript, 'escalate' to force escalation, or 'exit' to quit.")

#     while True:
#         q = input("You: ").strip()
#         if q.lower() in {"exit", "quit"}:
#             break
#         if q.lower() == "history":
#             print(get_history(sid))
#             continue
#         if q.lower().startswith("escalate"):
#             reason = q.split(" ", 1)[1] if " " in q else "Manual escalation"
#             print(escalate_session(sid, reason))
#             continue
#         resp = post_message(sid, q)
#         print("Bot:", resp["reply"])
#         print(f"(status={resp['status']}, conf={resp['confidence']}, cites={resp['citedFaqIds']})")



# Customer Support Bot (RAG + Memory + Escalation) using Gemini, PyPDFLoader, FAISS
# pip install -U langchain langchain-community langchain-google-genai faiss-cpu pypdf python-dotenv

import os
import time
import uuid
from typing import Dict, List, Optional

# --- Gemini via LangChain ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# --- PDF loading and chunking ---
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Vector store (FAISS) ---
from langchain_community.vectorstores import FAISS

# --- Prompt + message types ---
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage

# =========================
# Configuration
# =========================

API_KEY = "AIzaSyD3cklQJQxVJl9DOtonk7aXTDh8Y651mz0"
CHAT_MODEL = "gemini-2.5-flash"
EMBED_MODEL = "models/text-embedding-004"

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
TOP_K = 5
MAX_TURNS = 10

CONF_LOW_LEN = 25             # short answer → lower confidence
CONF_NO_HIT_PENALTY = 0.25    # no retrieved docs → penalty
ESCALATE_THRESHOLD = 0.45     # below this → escalation

# =========================
# Load Knowledge Base (PDF)
# =========================

PDF_PATH = r"C:\Users\Ishant Gupta\Downloads\kome-text.pdf"

loader = PyPDFLoader(PDF_PATH)
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
chunks = splitter.split_documents(pages)

emb = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=API_KEY)
vectordb = FAISS.from_documents(chunks, emb)
retriever = vectordb.as_retriever(search_kwargs={"k": TOP_K})

# =========================
# Session store (in-memory)
# =========================

Session = Dict[str, any]
Message = Dict[str, str]

SESSIONS: Dict[str, Session] = {}


def _now() -> float:
    return time.time()


def create_session(user_id: Optional[str] = None) -> Dict:
    sid = str(uuid.uuid4())
    SESSIONS[sid] = {
        "id": sid,
        "user_id": user_id or "demo-user",
        "status": "active",   # active | escalated | closed
        "history": [],        # list[HumanMessage | AIMessage]
        "created_at": _now(),
        "escalations": []     # list[{reason, at}]
    }
    return {"sessionId": sid, "status": "active"}


def get_history(session_id: str) -> Dict:
    s = SESSIONS[session_id]
    transcript: List[Message] = []
    for m in s["history"]:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        transcript.append({"role": role, "content": m.content})
    return {"messages": transcript}


def escalate_session(session_id: str, reason: str = "Low confidence"):
    s = SESSIONS[session_id]
    s["status"] = "escalated"
    s["escalations"].append({"reason": reason, "at": _now()})
    return {"status": "escalated", "ticketId": f"TKT-{session_id[:8]}".upper()}

# =========================
# Prompt + LLM client
# =========================

SYSTEM = """You are a helpful customer support assistant.
Use the provided context snippets from the company spec/FAQ when relevant.
If information is missing, ask one brief clarifying question or suggest the next actionable step.
When using a context snippet, cite its index like [1], [2].
Prefer concise, friendly answers with clear next actions when appropriate."""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    MessagesPlaceholder("history"),
    ("human", "User query: {question}\n\nContext:\n{context}\n\nAnswer:")
])

llm = ChatGoogleGenerativeAI(
    model=CHAT_MODEL,
    temperature=0.0,
    convert_system_message_to_human=True,
    google_api_key=API_KEY,
)


def _format_context(docs) -> str:
    lines = []
    for i, d in enumerate(docs, start=1):
        text = d.page_content
        if len(text) > 900:
            text = text[:900] + "..."
        lines.append(f"[{i}] {text}")
    return "\n".join(lines)


def _windowed(history: List, max_turns: int):
    return history[-max_turns:]


# =========================
# Confidence Scoring
# =========================
def _confidence(answer: str, hits: int) -> float:
    """Heuristic confidence score for demo purposes."""
    base = 0.7
    if len(answer.strip()) < CONF_LOW_LEN:
        base -= 0.3
    if hits == 0:
        base -= CONF_NO_HIT_PENALTY
    base = max(0.0, min(1.0, base))
    return base


# =========================
# Message Handling
# =========================
def post_message(session_id: str, content: str) -> Dict:
    s = SESSIONS[session_id]

    # 1) Retrieve context
    docs = retriever.invoke(content)
    ctx = _format_context(docs)

    # 2) Build message sequence
    history = _windowed(s["history"], MAX_TURNS)
    messages = prompt.format_messages(history=history, question=content, context=ctx)

    # 3) LLM inference
    ai = llm.invoke(messages)
    answer = ai.content or ""

    # 4) Confidence
    conf = _confidence(answer, hits=len(docs))
    status = s["status"]
    cited_ids = list(range(1, len(docs) + 1))

    # 5) Save history
    s["history"].append(HumanMessage(content=content))
    s["history"].append(AIMessage(content=answer))

    # 6) Escalation (if confidence below threshold)
    if conf < ESCALATE_THRESHOLD and status == "active":
        s["status"] = "escalated"
        s["escalations"].append({"reason": "Low confidence", "at": _now()})
        status = "escalated"
        answer += "\n\nIt looks like this needs review by a support agent. A ticket has been opened."

    return {
        "reply": answer,
        "citedFaqIds": cited_ids,
        "status": status,
        "confidence": round(conf, 2),
    }


# =========================
# CLI Demo
# =========================
if __name__ == "__main__":
    sess = create_session()
    sid = sess["sessionId"]
    print("Session:", sid, "- status:", sess["status"])
    print("Type 'history' to see transcript, 'escalate' to force escalation, or 'exit' to quit.")

    while True:
        q = input("You: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        if q.lower() == "history":
            print(get_history(sid))
            continue
        if q.lower().startswith("escalate"):
            reason = q.split(" ", 1)[1] if " " in q else "Manual escalation"
            print(escalate_session(sid, reason))
            continue
        resp = post_message(sid, q)
        print("Bot:", resp["reply"])
        print(f"(status={resp['status']}, conf={resp['confidence']}, cites={resp['citedFaqIds']})")

