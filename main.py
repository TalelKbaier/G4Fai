from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from enum import Enum
from g4f.client import Client

from database import Base, engine, get_db
from models import User, ChatSession, ChatHistory


class Model(str, Enum):
    gpt_5 = 'gpt-5-nano'
    gpt_4_nano = 'gpt-4.1-nano'
    deepseek = 'deepseek-r1-0528'
    ai = 'openai-fast'
    mistral = 'mistral-small-3.1-24b'
    gpt_4o_mini = "gpt-4o-mini"
    gpt_4 = "gpt-4"
    gemini_2_5 = 'gemini-2.5-flash-lite'
    gemini_pro = "gemini-2.5-flash"


default_model = Model.gpt_4_nano


app = FastAPI(title="g4f-ChatContext API", version="1.0.0")

API_PREFIX = "/api/v1"


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)



@app.get(f"{API_PREFIX}/create_user")
def create_user(db: Session = Depends(get_db)):
    new_user = User()
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user_id": new_user.user_id}



@app.get(f"{API_PREFIX}/create_session")
def create_session(user_id: str = None, db: Session = Depends(get_db)):
    if user_id:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Invalid user_id")
        new_session = ChatSession(user_id=user_id)
    else:
        new_session = ChatSession()

    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.session_id, "user_id": new_session.user_id}


@app.get(f"{API_PREFIX}/set_system_prompt")
def set_system_prompt(session_id: str, prompt: str, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    history_entry = ChatHistory(
        session_id=session_id,
        is_system_prompt=True,
        system_prompt=prompt
    )
    db.add(history_entry)
    db.commit()
    return {"status": "System prompt saved", "session_id": session_id, "prompt": prompt}


@app.get(f"{API_PREFIX}/chat")
def chat_with_bot(session_id: str, message: str, model: Model = default_model, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.id).all()
    messages = []
    for h in history:
        if h.is_system_prompt:
            messages.append({"role": "system", "content": h.system_prompt})
        else:
            if h.message_user:
                messages.append({"role": "user", "content": h.message_user})
            if h.response_bot:
                messages.append({"role": "assistant", "content": h.response_bot})

    messages.append({"role": "user", "content": message})

    client = Client()
    response = client.chat.completions.create(
        model=model.value,
        messages=messages,
        web_search=False
    )
    bot_reply = response.choices[0].message.content

    history_entry = ChatHistory(
        session_id=session_id,
        message_user=message,
        response_bot=bot_reply
    )
    db.add(history_entry)
    db.commit()

    return {
        "session_id": session_id,
        "user": message,
        "bot": bot_reply,
        "model_used": model,
        "user_id": session.user_id
    }


@app.get(f"{API_PREFIX}/history/{{session_id}}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.id).all()
    return [
        {"user": h.message_user, "bot": h.response_bot, "time": h.created_at}
        if not h.is_system_prompt
        else {"system": h.system_prompt, "time": h.created_at}
        for h in history
    ]


@app.get(f"{API_PREFIX}/sessions/{{user_id}}")
def get_user_sessions(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at).all()
    return [
        {"session_id": s.session_id, "created_at": s.created_at, "history_count": len(s.history)}
        for s in sessions
    ]


@app.get(f"{API_PREFIX}/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at).all()
    return [
        {"user_id": u.user_id, "created_at": u.created_at, "sessions_count": len(u.sessions)}
        for u in users
    ]


@app.get(f"{API_PREFIX}/user/{{user_id}}/stats")
def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    session_count = len(sessions)

    history_entries = (
        db.query(ChatHistory)
        .join(ChatSession, ChatHistory.session_id == ChatSession.session_id)
        .filter(ChatSession.user_id == user_id)
        .all()
    )
    total_messages = sum(
        (1 if h.message_user else 0) + (1 if h.response_bot else 0)
        for h in history_entries
    )
    system_prompts = sum(1 for h in history_entries if h.is_system_prompt)

    last_session_time = max([s.created_at for s in sessions], default=None)
    last_message_time = max([h.created_at for h in history_entries], default=None)

    return {
        "user_id": user.user_id,
        "created_at": user.created_at,
        "sessions_count": session_count,
        "total_messages": total_messages,
        "system_prompts": system_prompts,
        "last_session_time": last_session_time,
        "last_message_time": last_message_time,
    }


@app.get(f"{API_PREFIX}/stats/global")
def get_global_stats(db: Session = Depends(get_db)):
    users_count = db.query(User).count()
    sessions = db.query(ChatSession).all()
    sessions_count = len(sessions)
    history_entries = db.query(ChatHistory).all()

    total_messages = sum(
        (1 if h.message_user else 0) + (1 if h.response_bot else 0)
        for h in history_entries
    )
    system_prompts = sum(1 for h in history_entries if h.is_system_prompt)

    last_session_time = max([s.created_at for s in sessions], default=None)
    last_message_time = max([h.created_at for h in history_entries], default=None)

    return {
        "users_count": users_count,
        "sessions_count": sessions_count,
        "total_messages": total_messages,
        "system_prompts": system_prompts,
        "last_session_time": last_session_time,
        "last_message_time": last_message_time,
    }


@app.get(f"{API_PREFIX}/reset_db")
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return {"status": "Database reset successful"}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

