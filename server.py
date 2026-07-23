from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn
import logging
import sqlite3
import json
from typing import Optional, List

LOGGER = logging.getLogger("server")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="TECHPULSE-AI Backend API", version="2.5.0")

# Autoriser le Frontend React (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# SQLite Database Setup for Chat History Persistence
# ---------------------------------------------------------------------------
DB_PATH = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            msg_id INTEGER,
            role TEXT,
            content TEXT,
            intent TEXT,
            cves TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_message(msg_id: int, role: str, content: str, intent: str = "GENERAL_QUESTION", cves: List[str] = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (msg_id, role, content, intent, cves) VALUES (?, ?, ?, ?, ?)",
        (msg_id, role, content, intent, json.dumps(cves or []))
    )
    conn.commit()
    conn.close()

def get_all_messages():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT msg_id, role, content, intent, cves FROM messages ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "role": r[1],
            "content": r[2],
            "intent": r[3],
            "cves": json.loads(r[4]) if r[4] else []
        })
    return result

def clear_all_messages():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages")
    conn.commit()
    conn.close()

# ---------------------------------------------------------------------------
# API Schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    lang: str = "fr"

class LoginRequest(BaseModel):
    email: str
    password: str

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def read_root():
    return {"status": "online", "system": "TECHPULSE-AI RAG Server with SQLite Persistence"}

@app.post("/api/login")
async def login_endpoint(req: LoginRequest):
    # Flexible authentication for demo
    valid_emails = ["admin@techpulse.ai", "admin", "user@techpulse.ai"]
    valid_passwords = ["admin", "techpulse2026", "password"]

    if req.email in valid_emails or "@" in req.email:
        if req.password in valid_passwords or len(req.password) >= 4:
            return {
                "success": True,
                "token": "techpulse_bearer_token_2026_sec_suite",
                "user": {
                    "email": req.email,
                    "name": "Officier Sécurité Cyber",
                    "role": "Chief Information Security Officer (CISO)",
                    "agency": "Amadeus & Sabre Connector Ops"
                }
            }

    raise HTTPException(status_code=401, detail="Identifiants incorrects. Essayez avec admin@techpulse.ai / admin")

@app.get("/api/history")
async def get_history():
    messages = get_all_messages()
    return {"messages": messages}

@app.delete("/api/history")
async def delete_history():
    clear_all_messages()
    return {"status": "cleared", "message": "Historique des conversations réinitialisé avec succès."}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message
    if not user_msg:
        raise HTTPException(status_code=400, detail="Parameter 'message' is required.")

    # 1. Store User Message in SQLite
    user_msg_id = int(os.urandom(4).hex(), 16)
    save_message(user_msg_id, "user", user_msg)

    # 2. Generate Assistant Response
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    bot_response_text = ""
    bot_intent = "DYNAMIC"
    bot_cves = []

    if api_key:
        try:
            try:
                import google.genai as genai
                client = genai.Client(api_key=api_key)
                system_instruction = (
                    "Tu es TECHPULSE-AI, un assistant virtuel expert en cybersécurité pour le secteur du tourisme et du voyage. "
                    "Réponds de façon fluide, professionnelle, naturelle et adaptée à la demande de l'utilisateur. "
                    "Ne force PAS de template d'urgence si la question ne concerne pas un incident grave."
                )
                prompt = f"{system_instruction}\n\nQuestion de l'utilisateur ({req.lang}) : {user_msg}"
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                bot_response_text = response.text
            except Exception:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                system_instruction = (
                    "Tu es TECHPULSE-AI, un assistant virtuel expert en cybersécurité pour le secteur du tourisme et du voyage. "
                    "Réponds de façon fluide, professionnelle, naturelle et adaptée à la demande de l'utilisateur. "
                    "Ne force PAS de template d'urgence si la question ne concerne pas un incident grave."
                )
                prompt = f"{system_instruction}\n\nQuestion de l'utilisateur ({req.lang}) : {user_msg}"
                response = model.generate_content(prompt)
                bot_response_text = response.text
        except Exception as err:
            LOGGER.warning(f"Direct Gemini API error: {err}. Falling back to decision matrix.")

    # Dynamic fallback if no API response generated
    if not bot_response_text:
        q_lower = user_msg.lower()
        if any(g in q_lower.strip() for g in ["bonjour", "salut", "hello", "coucou", "hey"]):
            bot_response_text = "Bonjour ! 👋 Je suis TECHPULSE-AI, votre assistant virtuel en cybersécurité pour le secteur du voyage. Comment puis-je vous aider aujourd'hui ?"
            bot_intent = "GENERAL_QUESTION"
            bot_cves = []
        elif any(r in q_lower for r in ["rapport", "bilan", "24h", "dernières"]):
            bot_response_text = "📊 **Bilan d'activité des dernières 24h :**\n\n- **Alertes analysées :** 14 événements enregistrés.\n- **Statut API GDS :** Amadeus & Sabre 100% opérationnels.\n- **Sévérité :** Faible (0 menace critique)."
            bot_intent = "REPORT_REQUEST"
            bot_cves = []
        elif "cve" in q_lower:
            bot_response_text = "Une **CVE** (*Common Vulnerabilities and Exposures*) est un identifiant universel attribué aux vulnérabilités connues dans le secteur informatique et du voyage."
            bot_intent = "GENERAL_QUESTION"
            bot_cves = ["CVE-2025-0168"]
        else:
            bot_response_text = f"J'ai bien pris en compte votre demande concernant : *\"{user_msg}\"*.\n\nPour la sécurisation de vos accès GDS et connecteurs voyage, nos analyses préconisent l'application de filtres WAF stricts et le suivi des logs."
            bot_intent = "CYBER_QUESTION"
            bot_cves = []

    # 3. Store Assistant Message in SQLite
    bot_msg_id = user_msg_id + 1
    save_message(bot_msg_id, "assistant", bot_response_text, bot_intent, bot_cves)

    return {
        "response": bot_response_text,
        "intent": bot_intent,
        "cves": bot_cves
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000)
