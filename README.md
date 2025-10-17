# 🤖 AI Customer Support Bot (Unthinkable Solutions Demo)

This project is a smart AI Customer Support Chatbot built using **Google Gemini**, **RAG (Retrieval-Augmented Generation)**, **FAISS**, and **Streamlit**.

It demonstrates how an intelligent support system can provide contextual, document-backed responses and handle low-confidence queries with escalation.

## Links
- Drive : https://drive.google.com/file/d/1AhkVBhRib8LLcGq9qV3e8Jqy4bLwRiir/view?usp=sharing
- Demo video : https://drive.google.com/file/d/15w-DsXcD0pE2AHmoPjEMRmOef7I32RB_/view?usp=sharing

---

## 🧩 Features
- RAG-based document retrieval (via FAISS)
- Contextual memory and chat history
- Confidence scoring + escalation simulation
- FastAPI backend + Streamlit frontend
- Gemini model integration for high-quality answers

---

## 🧠 Tech Stack
- **LLM:** Gemini (via LangChain)
- **Database:** FAISS Vector Store
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Knowledge Base:** Company PDF (e.g. product FAQs)

---

## Demo Questions
- My spouse and I both have the same card number. How does Verified by Visa/ MasterCard SecureCode work for both of us?
- what is NET SAFE?
- while tryinh to register i am getting error message card - *error message*
- can i register all of your HDFC bank master card or visa card?
- How do I register my HDFC Bank Card?

## 🚀 Run Locally

### 1️⃣ Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # on Windows

 Backend Requirements
Navigate to the backend folder:
cd backend

