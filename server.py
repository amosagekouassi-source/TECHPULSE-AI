from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
import uvicorn
import logging
import sqlite3
import json
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()  # Charge toutes les variables du .env (GEMINI_*, GROQ_API_KEY, etc.)


LOGGER = logging.getLogger("server")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="TECHPULSE-AI Backend API", version="2.9.0")

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
# Multi-Key API Rotation Helper
# ---------------------------------------------------------------------------
def get_api_keys() -> List[str]:
    """Rotation multi-clés sur 3 projets indépendants (3 quotas distincts)."""
    keys = []
    vars_ordered = [
        "GEMINI_API_KEY",    # Projet 1 (gen-lang-client-0619309865)
        "GEMINI_API_KEY_2",  # Projet 2 (project-2689a467)
        "GEMINI_API_KEY_3",  # Projet 3 (gen-lang-client-0886497355)
        "GEMINI_API_KEY_4",  # Projet 2 — clé secondaire
        "GEMINI_API_KEY_5",  # Projet 1 — clé secondaire
        "GOOGLE_API_KEY",    # Clé générique optionnelle
    ]
    for var in vars_ordered:
        val = os.getenv(var)
        if val and val.strip() and val.strip() not in keys:
            keys.append(val.strip())
    return keys


def call_llm(prompt: str) -> str:
    """Appelle Gemini (rotation multi-clés) puis Groq en fallback automatique."""

    # — Tentatives Gemini (toutes les clés disponibles) —
    for key in get_api_keys():
        try:
            try:
                import google.genai as genai
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model="models/gemini-2.0-flash",
                    contents=prompt
                )
                return response.text
            except Exception:
                import google.generativeai as genai2
                genai2.configure(api_key=key)
                model = genai2.GenerativeModel("gemini-1.5-flash")
                return model.generate_content(prompt).text
        except Exception as err:
            if "429" in str(err) or "EXHAUSTED" in str(err) or "quota" in str(err).lower():
                LOGGER.debug(f"Gemini quota hit, trying next key...")
                continue
            LOGGER.warning(f"Gemini error: {err}")

    # — Fallback Groq (gratuit, très rapide) —
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            LOGGER.info("Reponse via Groq (fallback Gemini quota epuise)")
            return response.choices[0].message.content
        except Exception as err:
            LOGGER.error(f"Groq fallback error: {err}")

    return ""


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
    return {"status": "online", "system": "TECHPULSE-AI RAG Server V2.9 (LLM-First + RAG Context)"}

@app.post("/api/login")
async def login_endpoint(req: LoginRequest):
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

    # 2. RAG context injection (FAISS) — enrichit le prompt Gemini avec des documents pertinents
    rag_context = ""
    detected_cves = []
    try:
        from app.vector_store.faiss_store import FAISSVectorStore
        from pathlib import Path
        store = FAISSVectorStore(index_dir=Path("models/vector_store"))
        matches = store.search(user_msg, k=3)
        if matches:
            rag_context = "\n\n---\nContexte RAG (documents de sécurité pertinents) :\n"
            for m in matches:
                text = m.get("text", m.get("content", ""))
                if text:
                    rag_context += f"- {text[:300]}\n"
            for m in matches:
                found = re.findall(r"CVE-\d{4}-\d+", m.get("text", m.get("content", "")), re.IGNORECASE)
                detected_cves.extend(found)
            detected_cves = list(dict.fromkeys(detected_cves))  # déduplique en gardant l'ordre
    except Exception as rag_err:
        LOGGER.debug(f"RAG context unavailable (index not built yet): {rag_err}")

    # 3. Gemini raisonne librement — system prompt riche, zéro if/elif de contenu
    lang_label = "français" if req.lang == "fr" else "english"
    system_instruction = (
        f"Tu es TECHPULSE-AI, la plateforme SaaS d'intelligence cyber et de monitoring en temps réel dédiée au secteur du voyage. "
        f"Tu maîtrises : les API GDS (Amadeus, Sabre, Galileo, Travelport), la conformité PCI-DSS, "
        f"les CVE/CVSS, l'analyse d'incidents cyber (ransomware, RCE, phishing, injection SQL, zero-day), "
        f"la sécurisation des passerelles de paiement et des connecteurs de réservation. "
        f"RÈGLE CRITIQUE DE POSTURE : "
        f"1. Donne TOUJOURS des recommandations et actions concrètes que l'utilisateur doit appliquer lui-même (ex: patcher un système, isoler un serveur, configurer un pare-feu). "
        f"2. MAIS, pour tout ce qui concerne la SURVEILLANCE, le MONITORING ou la DÉTECTION, ne dis jamais à l'utilisateur de s'en occuper. C'est TON rôle natif. "
        f"Exemple : Au lieu de dire 'Mettez en place un monitoring', dis 'TECHPULSE-AI surveille déjà vos endpoints GDS en temps réel pour bloquer toute récidive.' "
        f"Réponds TOUJOURS de façon structurée, précise et contextualisée au secteur du voyage. "
        f"Si la question est générale (ex: 'Qu'est-ce qu'une CVE ?'), explique clairement le concept "
        f"puis donne un exemple concret lié au secteur du voyage. "
        f"Utilise des emojis et du markdown pour rendre la réponse lisible. "
        f"Langue de réponse : {lang_label}."
    )

    bot_response_text = ""
    bot_intent = "GENERAL_QUESTION"
    bot_cves = detected_cves

    bot_response_text = call_llm(f"{system_instruction}\n\nQuestion : {user_msg}{rag_context}")
    if bot_response_text:
        bot_intent = "DYNAMIC"

    # 4. Fallback minimal si l'API Gemini est totalement indisponible
    if not bot_response_text:
        LOGGER.error("All Gemini API keys failed. Check GEMINI_API_KEY in .env")
        bot_response_text = (
            "⚠️ Le moteur IA (Gemini) est temporairement indisponible.\n\n"
            "Vérifiez que votre clé API (`GEMINI_API_KEY`) dans le fichier `.env` est valide "
            "et que votre quota n'est pas épuisé sur [Google AI Studio](https://aistudio.google.com/apikey)."
        )
        bot_intent = "ERROR"

    # 5. Store Assistant Message in SQLite
    bot_msg_id = user_msg_id + 1
    save_message(bot_msg_id, "assistant", bot_response_text, bot_intent, bot_cves)

    return {
        "response": bot_response_text,
        "intent": bot_intent,
        "cves": bot_cves
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
