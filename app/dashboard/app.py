"""Conversational Cybersecurity Chatbot Assistant for TECHPULSE-AI (Demo Day)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Resolve project root and prevent current directory name collisions
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DASHBOARD_DIR = str(Path(__file__).resolve().parent)
if DASHBOARD_DIR in sys.path:
    sys.path.remove(DASHBOARD_DIR)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.rag.pipeline import RAGPipeline

# Page setup
st.set_page_config(
    page_title="TECHPULSE-AI | Assistant Cybersécurité",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics
st.markdown(
    """
    <style>
    .main {
        background-color: #0E1117;
    }
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .header-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .header-title {
        color: #38BDF8;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 1rem;
        margin-top: 0.3rem;
    }
    .status-used {
        color: #22C55E;
        font-weight: 700;
    }
    .status-unused {
        color: #64748B;
        font-weight: 400;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
    }
    .intent-THREAT_ANALYSIS {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
    }
    .intent-BUSINESS_ADVICE {
        background-color: rgba(56, 189, 248, 0.2);
        color: #38BDF8;
        border: 1px solid #38BDF8;
    }
    .intent-GENERAL {
        background-color: rgba(148, 163, 184, 0.2);
        color: #94A3B8;
        border: 1px solid #94A3B8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_rag_pipeline() -> RAGPipeline:
    """Initialize and retrieve the RAGPipeline instance."""
    if "rag_pipeline" not in st.session_state or not hasattr(st.session_state.rag_pipeline, "process_chat_message"):
        st.session_state.rag_pipeline = RAGPipeline()
    return st.session_state.rag_pipeline


def main() -> None:
    """Render Streamlit Chatbot Assistant UI."""
    pipeline = get_rag_pipeline()

    # Session State Initialization
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Bonjour ! Je suis **TECHPULSE-AI**, votre assistant cybersécurité spécialisé pour les agences "
                    "de voyage, plateformes de réservation et billetteries.\n\n"
                    "Comment puis-je vous aider aujourd'hui ? Vous pouvez me poser une question générale, "
                    "demander un conseil métier, ou me décrire une menace/incident détecté."
                ),
            }
        ]

    if "last_intent" not in st.session_state:
        st.session_state.last_intent = "N/A"

    if "last_modules" not in st.session_state:
        st.session_state.last_modules = {"distilbert": False, "faiss": False, "llm": True}

    # Header Banner
    st.markdown(
        """
        <div class="header-box">
            <h1 class="header-title">🛡️ TECHPULSE-AI</h1>
            <p class="header-subtitle">
                Assistant Cybersécurité Conversationnel pour le Secteur du Tourisme & de la Réservation
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar
    st.sidebar.image("https://img.icons8.com/isometric/100/shield.png", width=65)
    st.sidebar.title("TECHPULSE Controls")

    # Module Status Indicator for Last Query
    st.sidebar.markdown("### 📊 État des Modules (Dernière réponse)")

    intent = st.session_state.last_intent
    if intent != "N/A":
        intent_labels = {
            "THREAT_ANALYSIS": "🚨 Analyse de Menace",
            "BUSINESS_ADVICE": "💼 Conseil Métier",
            "GENERAL": "❓ Question Générale",
        }
        st.sidebar.markdown(
            f'<div class="intent-badge intent-{intent}">{intent_labels.get(intent, intent)}</div>',
            unsafe_allow_html=True,
        )

    mods = st.session_state.last_modules

    distil_status = '<span class="status-used">✓ Utilisé</span>' if mods.get("distilbert") else '<span class="status-unused">○ Non utilisé</span>'
    faiss_status = '<span class="status-used">✓ Utilisé</span>' if mods.get("faiss") else '<span class="status-unused">○ Non utilisé</span>'
    llm_status = '<span class="status-used">✓ Utilisé (Gemini)</span>' if mods.get("llm") else '<span class="status-unused">○ Non utilisé</span>'

    st.sidebar.markdown(f"- **DistilBERT Classifier** : {distil_status}", unsafe_allow_html=True)
    st.sidebar.markdown(f"- **FAISS Vector Store** : {faiss_status}", unsafe_allow_html=True)
    st.sidebar.markdown(f"- **LLM Generator** : {llm_status}", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Exemples d'interactions")

    preset_input = None
    if st.sidebar.button("🚨 Menace : RCE API Réservation"):
        preset_input = "Nous avons détecté une vulnérabilité critique d'exécution de code à distance (RCE) sur notre API de réservation."
    if st.sidebar.button("💼 Conseil : Risques Agences"):
        preset_input = "Quels sont les principaux risques cyber qui concernent les agences de voyage ?"
    if st.sidebar.button("❓ Général : Qu'est-ce qu'une CVE ?"):
        preset_input = "Qu'est-ce qu'une CVE ?"

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Réinitialiser la conversation"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Bonjour ! Je suis **TECHPULSE-AI**, votre assistant cybersécurité spécialisé. "
                    "La conversation a été réinitialisée. Comment puis-je vous aider ?"
                ),
            }
        ]
        st.session_state.last_intent = "N/A"
        st.session_state.last_modules = {"distilbert": False, "faiss": False, "llm": True}
        st.rerun()

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input Zone
    user_input = st.chat_input("Posez votre question à TECHPULSE-AI...") or preset_input

    if user_input:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process via RAG Pipeline
        with st.chat_message("assistant"):
            with st.spinner("TECHPULSE-AI réfléchit..."):
                response_data = pipeline.process_chat_message(
                    query=user_input,
                    history=st.session_state.messages[:-1],
                )

            answer = response_data["response_text"]
            st.markdown(answer)

            # Store state for sidebar
            st.session_state.last_intent = response_data["intent"]
            st.session_state.last_modules = response_data["modules_used"]
            st.session_state.messages.append({"role": "assistant", "content": answer})

            # Force rerun to update sidebar indicators immediately
            st.rerun()


if __name__ == "__main__":
    main()
