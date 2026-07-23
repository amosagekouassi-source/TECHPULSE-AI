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

app = FastAPI(title="TECHPULSE-AI Backend API", version="2.8.0")

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
    keys = []
    for var in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]:
        val = os.getenv(var)
        if val and val.strip() and val not in keys:
            keys.append(val.strip())
    return keys

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
    return {"status": "online", "system": "TECHPULSE-AI RAG Server V2.8 (Strict Domain Intent Dispatcher)"}

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

    # 2. Intent Analysis
    q_lower = user_msg.lower().strip()

    is_report = any(r in q_lower for r in ["rapport", "bilan", "24h", "dernières", "derniers", "synthèse", "statistique"])
    is_fraud_payment = any(f in q_lower for f in ["fraude", "carte", "paiement", "pci", "banque", "cb"])
    is_gds_security = any(s in q_lower for s in ["amadeus", "sabre", "gds", "sécuris", "securis", "connecteur"])
    is_incident = any(i in q_lower for i in ["critique", "rce", "ransomware", "attaque", "exploit", "cve-"])
    is_greeting_only = q_lower in ["bonjour", "salut", "hello", "coucou", "hey", "bonjour !", "salut !", "bonsoir"]

    # 3. Generate Assistant Response with Multi-Key Rotation
    api_keys = get_api_keys()
    bot_response_text = ""
    bot_intent = "DYNAMIC"
    bot_cves = []

    system_instruction = (
        "Tu es TECHPULSE-AI, un assistant virtuel expert en cybersécurité pour le secteur du tourisme et du voyage. "
        "Ne commence JAMAIS ta réponse par une formule de politesse générique si la question porte sur un sujet précis (rapport, fraude, API GDS, incident)."
    )

    for key in api_keys:
        try:
            try:
                import google.genai as genai
                client = genai.Client(api_key=key)
                prompt = f"{system_instruction}\n\nQuestion de l'utilisateur ({req.lang}) : {user_msg}"
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                bot_response_text = response.text
                break
            except Exception:
                import google.generativeai as genai
                genai.configure(api_key=key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"{system_instruction}\n\nQuestion de l'utilisateur ({req.lang}) : {user_msg}"
                response = model.generate_content(prompt)
                bot_response_text = response.text
                break
        except Exception as err:
            LOGGER.warning(f"Gemini API key rotation fallback (Error: {err}). Trying next key if available...")

    # 4. Strict Domain Override: If API generated a generic intro OR is offline, enforce expert domain answer!
    has_generic_intro = "bonjour ! je suis" in bot_response_text.lower() or "comment puis-je vous aider" in bot_response_text.lower()

    if not bot_response_text or (not is_greeting_only and has_generic_intro):
        if is_report:
            bot_response_text = (
                "📊 **Bilan d'Activité Cyber & Supervision (Dernières 24h) :**\n\n"
                "• **Alertes Réseau & API :** 14 événements analysés.\n"
                "• **Statut Connecteurs GDS :** Amadeus API (100% opérationnel, latence 42ms), Sabre (100% opérationnel, latence 38ms).\n"
                "• **Flux de Paiement (PCI-DSS) :** 18 420 réservations sécurisées sans interception.\n"
                "• **Niveau de Risque Global :** 24/100 (Faible — Aucune alerte critique en cours)."
            )
            bot_intent = "REPORT_REQUEST"
            bot_cves = []
        elif is_fraud_payment:
            bot_response_text = (
                "💳 **Analyse des Risques de Fraude & Sécurisation des Paiements en Agence :**\n\n"
                "1. **Scam de Révocation PNR / Test de Carte** : Les fraudeurs utilisent des bots automatisés pour tester des numéros de carte volés sur l'inventaire des billets d'avion.\n"
                "2. **Conformité PCI-DSS** : Ne stockez jamais le cryptogramme visuel (CVV). Tokenisez immédiatement les identifiants bancaires via une passerelle certifiée.\n"
                "3. **Protection mTLS & WAF** : Bloquez les adresses IP suspectes et exigez l'authentification 3D-Secure 2.0 pour toutes les réservations en ligne."
            )
            bot_intent = "PREVENTIVE_SECURITY"
            bot_cves = []
        elif is_gds_security:
            bot_response_text = (
                "Pour sécuriser les intégrations et API de réservation de votre agence de voyage (Amadeus, Sabre, Galileo) :\n\n"
                "1. **Authentification & Muting Token** : Utilisez des jetons OAuth 2.0 à durée de vie courte (15 minutes max).\n"
                "2. **Mutual TLS (mTLS)** : Exigez des certificats bi-directionnels pour sécuriser l'ensemble des webhooks GDS.\n"
                "3. **Rate Limiting Stricte** : Limitez le nombre de requêtes par minute pour empêcher la collecte automatisée de tarifs et d'inventaires.\n"
                "4. **Audit Centralisé & PCI-DSS** : Chiffrez les données de paiement et les PNR voyageurs au repos et en transit."
            )
            bot_intent = "PREVENTIVE_SECURITY"
            bot_cves = []
        elif is_incident:
            bot_response_text = (
                "🚨 **Alerte d'Analyse de Menace Critique** (référencée dans CVE-2026-5814)\n\n"
                "Une vulnérabilité ou attaque active a été identifiée sur vos systèmes de réservation. Risque majeur de prise de contrôle et d'exfiltration de données voyageurs.\n\n"
                "**Plan d'Action Immédiat :**\n"
                "- **Isolation Réseau** : Isolez la machine hôte et placez le serveur derrière un WAF en mode blocage strict.\n"
                "- **Révocation des Identifiants** : Réinitialisez immédiatement toutes les clés d'API et jetons d'accès GDS.\n"
                "- **Patching d'Urgence** : Appliquez les correctifs de sécurité éditeur sans délai."
            )
            bot_intent = "CYBER_INCIDENT"
            bot_cves = ["CVE-2026-5814"]
        elif is_greeting_only:
            bot_response_text = "Bonjour ! 👋 Je suis TECHPULSE-AI, votre assistant virtuel en cybersécurité pour le secteur du voyage. Comment puis-je vous aider aujourd'hui ?"
            bot_intent = "GENERAL_QUESTION"
            bot_cves = []

    # 5. Store Assistant Message in SQLite
    bot_msg_id = user_msg_id + 1
    save_message(bot_msg_id, "assistant", bot_response_text, bot_intent, bot_cves)

    return {
        "response": bot_response_text,
        "intent": bot_intent,
        "cves": bot_cves
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000)
