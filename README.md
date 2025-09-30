# 💬 g4f-ChatContext API

🚀 A **lightweight chat backend** built on **g4f**, designed to quickly create and manage **conversation context** and allow seamless **return to history**.

---

## ✨ Features

* ⚡ **Lightweight & Fast**

  * Minimal dependencies, optimized for speed.
* 👤 **User Management**

  * Create anonymous or persistent users (UUID-based).
* 💬 **Chat Sessions**

  * Start new sessions (linked to a user or temporary).
  * Save conversation history with system prompts, user messages, and bot responses.
* 🤖 **Multi-Model Support**

  * GPT-4, GPT-5 Nano, Mistral, DeepSeek, Gemini, etc.

* 📌 **Versioned API**

  * All endpoints are prefixed with `/api/v1/` for easy future upgrades.

---

## 📂 Project Structure

```
.
├── main.py          # FastAPI app
├── models.py        # SQLAlchemy ORM models (User, ChatSession, ChatHistory)
├── database.py      # Database engine & session
├── requirements.txt # Python dependencies
└── README.md        # Project documentation
```

---

## ⚙️ Installation

### 1️⃣ Clone the repo

```bash
git clone https://github.com/your-username/g4f-chatcontext-api.git
cd g4f-chatcontext-api
```

### 2️⃣ Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the API

```bash
uvicorn main:app --reload
```

API will be available at:
👉 `http://127.0.0.1:8000`

Interactive docs:
👉 `http://127.0.0.1:8000/docs`

---

## 🔌 API Endpoints

### 👤 Users

* `GET /api/v1/create_user` → Create new user
* `GET /api/v1/users` → List all users
* `GET /api/v1/user/{user_id}/stats` → User statistics

### 💬 Sessions

* `GET /api/v1/create_session?user_id=...` → Create new chat session
* `GET /api/v1/sessions/{user_id}` → List user sessions
* `GET /api/v1/set_system_prompt` → Set system prompt

### 🤖 Chat

* `GET /api/v1/chat?session_id=...&message=...` → Chat with AI
* `GET /api/v1/history/{session_id}` → Get chat history

### 📊 Stats

* `GET /api/v1/stats/global` → Global statistics

### ⚠️ Development

* `GET /api/v1/reset_db` → Reset database (dev only)

---

## 📦 Example Requests

### Create user

```bash
curl http://127.0.0.1:8000/api/v1/create_user
```

### Create session

```bash
curl "http://127.0.0.1:8000/api/v1/create_session?user_id=<USER_ID>"
```

### Chat with bot

```bash
curl "http://127.0.0.1:8000/api/v1/chat?session_id=<SESSION_ID>&message=Hello"
```

---

## 🧩 Supported Models

* `gpt-5-nano`
* `gpt-4.1-nano`
* `deepseek-r1-0528`
* `openai-fast`
* `mistral-small-3.1-24b`
* `gpt-4o-mini`
* `gpt-4`
* `gemini-2.5-flash-lite`
* `gemini-2.5-flash`

---

## 📜 License

MIT License © 2025


