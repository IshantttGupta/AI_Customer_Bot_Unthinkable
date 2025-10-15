# # import streamlit as st
# # import requests

# # # -----------------------------
# # # CONFIGURATION
# # # -----------------------------
# # BACKEND_URL = "http://127.0.0.1:8000/chat"  # we'll make this backend later

# # # -----------------------------
# # # STREAMLIT PAGE SETUP
# # # -----------------------------
# # st.set_page_config(page_title="AI Customer Support Bot", page_icon="🤖")
# # st.title("🤖 AI Customer Support Chatbot")
# # st.write("Ask any question below. The bot uses RAG + Gemini + Memory to answer contextually.")

# # # -----------------------------
# # # CHAT HISTORY HANDLING
# # # -----------------------------
# # if "history" not in st.session_state:
# #     st.session_state.history = []  # list of dicts: {"role": "user"/"bot", "text": "..."}

# # # -----------------------------
# # # USER INPUT
# # # -----------------------------
# # user_input = st.text_input("Type your message:")

# # if st.button("Send"):
# #     if user_input.strip() == "":
# #         st.warning("Please type something before sending.")
# #     else:
# #         # Add user message to history
# #         st.session_state.history.append({"role": "user", "text": user_input})

# #         # -----------------------------
# #         # CALL BACKEND
# #         # -----------------------------
# #         try:
# #             res = requests.post(BACKEND_URL, json={"query": user_input})
# #             if res.status_code == 200:
# #                 bot_reply = res.json().get("reply", "No response from backend.")
# #             else:
# #                 bot_reply = f"Error {res.status_code}: {res.text}"
# #         except Exception as e:
# #             bot_reply = f"⚠️ Cannot connect to backend: {e}"

# #         # Add bot reply to history
# #         st.session_state.history.append({"role": "bot", "text": bot_reply})

# # # -----------------------------
# # # DISPLAY CHAT MESSAGES
# # # -----------------------------
# # st.markdown("### 💬 Conversation:")
# # for msg in st.session_state.history:
# #     if msg["role"] == "user":
# #         st.markdown(f"🧑 You: {msg['text']}")
# #     else:
# #         st.markdown(f"🤖 Bot: {msg['text']}")


# import streamlit as st
# import requests

# # Backend endpoints
# BASE_URL = "http://127.0.0.1:8000"
# CHAT_URL = f"{BASE_URL}/chat"
# SESSION_URL = f"{BASE_URL}/create_session"

# st.set_page_config(page_title="AI Customer Support Bot", page_icon="🤖")
# st.title("🤖 AI Customer Support Chatbot")
# st.write("Ask your question below. The bot uses Gemini + RAG + Memory + Escalation.")

# # Create or reuse session
# if "session_id" not in st.session_state:
#     res = requests.post(SESSION_URL)
#     st.session_state.session_id = res.json()["sessionId"]

# if "history" not in st.session_state:
#     st.session_state.history = []

# # User input
# user_input = st.text_input("Type your message:")

# if st.button("Send") and user_input.strip():
#     st.session_state.history.append({"role": "user", "text": user_input})
#     try:
#         payload = {"query": user_input, "session_id": st.session_state.session_id}
#         res = requests.post(CHAT_URL, json=payload)
#         reply = res.json().get("reply", "")
#         st.session_state.history.append({"role": "bot", "text": reply})
#     except Exception as e:
#         st.session_state.history.append({"role": "bot", "text": f"⚠️ Error: {e}"})

# # Display chat
# st.markdown("### 💬 Conversation:")
# for msg in st.session_state.history:
#     if msg["role"] == "user":
#         st.markdown(f"🧑 **You:** {msg['text']}")
#     else:
#         st.markdown(f"🤖 **Bot:** {msg['text']}")

import streamlit as st
import requests
from datetime import datetime

# =========================
# CONFIGURATION
# =========================
BASE_URL = "http://127.0.0.1:8000"
CHAT_URL = f"{BASE_URL}/chat"
SESSION_URL = f"{BASE_URL}/create_session"

st.set_page_config(page_title="AI Banking Customer Support Bot", page_icon="🤖", layout="centered")

# =========================
# AQUA & BLACK THEME STYLING
# =========================
st.markdown(
    """
    <style>
    /* Global Dark Theme */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #0a0a0a 50%, #001a1a 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Header */
    .main-header {
        background: linear-gradient(135deg, #00d9ff 0%, #00ffcc 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 217, 255, 0.4);
    }
    
    .main-header h1 {
        color: #000000;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0, 255, 204, 0.3);
    }
    
    .main-header p {
        color: #001a1a;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.8;
        font-weight: 500;
    }
    
    /* Input Section */
    .input-section {
        background: rgba(0, 26, 26, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(0, 217, 255, 0.1);
    }
    
    .input-section h3 {
        color: #00ffcc;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Streamlit Input Customization */
    .stTextInput > div > div > input {
        background-color: #0a0a0a !important;
        color: #00ffcc !important;
        border: 2px solid #003333 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d9ff !important;
        box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #006666 !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #00d9ff 0%, #00ffcc 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 217, 255, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 217, 255, 0.6) !important;
        background: linear-gradient(135deg, #00ffcc 0%, #00d9ff 100%) !important;
    }
    
    /* Clear Button */
    div[data-testid="column"]:nth-child(2) .stButton > button {
        background: rgba(255, 0, 100, 0.1) !important;
        color: #ff0066 !important;
        border: 2px solid #ff0066 !important;
    }
    
    div[data-testid="column"]:nth-child(2) .stButton > button:hover {
        background: #ff0066 !important;
        color: white !important;
    }
    
    /* Chat Container */
    .chat-container {
        background: rgba(0, 26, 26, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
        box-shadow: 0 4px 16px rgba(0, 217, 255, 0.1);
    }
    
    /* Message Bubbles */
    .user-msg {
        background: linear-gradient(135deg, #00d9ff 0%, #00ffcc 100%);
        color: #000000;
        border-radius: 18px 18px 4px 18px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        margin-left: auto;
        width: fit-content;
        max-width: 75%;
        box-shadow: 0 4px 12px rgba(0, 217, 255, 0.4);
        animation: slideInRight 0.3s ease;
    }
    
    .bot-msg {
        background: rgba(0, 26, 26, 0.8);
        color: #00ffcc;
        border-radius: 18px 18px 18px 4px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        margin-right: auto;
        width: fit-content;
        max-width: 75%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(0, 217, 255, 0.3);
        animation: slideInLeft 0.3s ease;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .message-label {
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
        opacity: 0.9;
    }
    
    .message-text {
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .confidence {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        padding: 0.25rem 0.75rem;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 12px;
        font-weight: 600;
    }
    
    .timestamp {
        font-size: 0.75rem;
        opacity: 0.6;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Scrollbar Styling */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(0, 26, 26, 0.3);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(0, 217, 255, 0.5);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 217, 255, 0.7);
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #006666;
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .user-msg, .bot-msg {
            max-width: 90%;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HEADER
# =========================
st.markdown(
    """
    <div class="main-header">
        <h1>🤖 AI Banking Customer Support</h1>
        <p>Powered by Gemini + RAG + Memory + Smart Escalation</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# SESSION MANAGEMENT
# =========================
if "session_id" not in st.session_state:
    try:
        res = requests.post(SESSION_URL)
        st.session_state.session_id = res.json()["sessionId"]
    except:
        st.session_state.session_id = "demo-session"

if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# INPUT SECTION
# =========================
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.markdown('<h3>Ask a Question</h3>', unsafe_allow_html=True)

user_input = st.text_input(
    "Type your message:",
    placeholder="How can I reset my password?",
    key="input_box",
    label_visibility="collapsed"
)

col1, col2 = st.columns([4, 1])
with col1:
    send_clicked = st.button("Send Message", use_container_width=True)
with col2:
    clear_clicked = st.button("Clear", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HANDLE CLEAR CHAT
# =========================
if clear_clicked:
    st.session_state.history = []
    st.rerun()

# =========================
# SEND MESSAGE
# =========================
if send_clicked and user_input.strip():
    st.session_state.history.append({
        "role": "user",
        "text": user_input,
        "time": datetime.now().strftime("%H:%M")
    })

    try:
        payload = {"query": user_input, "session_id": st.session_state.session_id}
        res = requests.post(CHAT_URL, json=payload)
        data = res.json()

        reply = data.get("reply", "⚠️ No response received.")
        confidence = data.get("confidence", 0)
        status = data.get("status", "active")

        conf_color = "#00ffcc" if confidence >= 0.75 else "#ffcc00" if confidence >= 0.45 else "#ff0066"
        conf_label = f"<span style='color:{conf_color};'>{confidence*100:.1f}%</span>"

        st.session_state.history.append({
            "role": "bot",
            "text": reply,
            "confidence": conf_label,
            "status": status,
            "time": datetime.now().strftime("%H:%M")
        })

    except Exception as e:
        st.session_state.history.append({
            "role": "bot",
            "text": f"⚠️ Connection Error: {str(e)}",
            "confidence": None,
            "time": datetime.now().strftime("%H:%M")
        })
    
    st.rerun()

# =========================
# DISPLAY CHAT
# =========================
# Render messages directly without empty space
st.markdown('<div style="padding: 0; margin-top: 1rem;">', unsafe_allow_html=True)

if not st.session_state.history:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <p>No messages yet. Start a conversation!</p>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="user-msg">
                    <div class="message-label">👤 You</div>
                    <div class="message-text">{msg['text']}</div>
                    <div class="timestamp">{msg['time']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            confidence_html = f"<div class='confidence'>Confidence: {msg['confidence']}</div>" if msg.get("confidence") else ""
            st.markdown(
                f"""
                <div class="bot-msg">
                    <div class="message-label">🤖 Assistant</div>
                    <div class="message-text">{msg['text']}</div>
                    {confidence_html}
                    <div class="timestamp">{msg['time']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("</div>", unsafe_allow_html=True)