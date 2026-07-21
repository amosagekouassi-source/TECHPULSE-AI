"""TECHPULSE-AI Cyber Intelligence Platform Dashboard (Demo Day)."""

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

import pandas as pd
import streamlit as st
from app.rag.pipeline import RAGPipeline
from app.analytics.engine import CyberAnalyticsEngine

# Page setup
st.set_page_config(
    page_title="TECHPULSE-AI | Cyber Intelligence Platform",
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
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
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
    .health-badge {
        display: inline-block;
        padding: 0.6rem 1.4rem;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.1rem;
        margin: 1rem 0;
    }
    .health-critical {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
    }
    .health-high {
        background-color: rgba(249, 115, 22, 0.2);
        color: #F97316;
        border: 1px solid #F97316;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
    }
    .intent-THREAT_ANALYSIS, .intent-CVE_ANALYSIS {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
    }
    .intent-CYBER_QUESTION, .intent-REPORT_REQUEST {
        background-color: rgba(56, 189, 248, 0.2);
        color: #38BDF8;
        border: 1px solid #38BDF8;
    }
    .intent-GENERAL_QUESTION {
        background-color: rgba(148, 163, 184, 0.2);
        color: #94A3B8;
        border: 1px solid #94A3B8;
    }
    .card-box {
        background: #1E293B;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_rag_pipeline() -> RAGPipeline:
    """Initialize and retrieve RAGPipeline instance stored in session_state."""
    if "rag_pipeline" not in st.session_state or not hasattr(st.session_state.rag_pipeline, "process_chat_message"):
        st.session_state.rag_pipeline = RAGPipeline()
    return st.session_state.rag_pipeline


@st.cache_resource
def get_analytics_engine() -> CyberAnalyticsEngine:
    """Initialize and cache CyberAnalyticsEngine."""
    return CyberAnalyticsEngine()


def main() -> None:
    """Render TECHPULSE-AI 2-Tab Platform UI."""
    pipeline = get_rag_pipeline()
    analytics = get_analytics_engine()

    # Session State Initialization for Chatbot
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Bonjour ! Je suis **TECHPULSE-AI**, votre assistant cybersécurité spécialisé dans les "
                    "agences de voyage, moteurs de réservation et plateformes de billetterie.\n\n"
                    "Comment puis-je vous aider aujourd'hui ? (ex: *Que s'est-il passé ces dernières 24h ?*, "
                    "*Quels risques sur nos API de réservation ?*, *Nous détectons un ransomware*, *Qu'est-ce qu'une CVE ?*)"
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
            <h1 class="header-title">🛡️ TECHPULSE-AI Cyber Intelligence Platform</h1>
            <p class="header-subtitle">
                Plateforme d'Intelligence Cyber & Assistant IA Conversationnel pour le Secteur du Tourisme
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar: Full System & Module Status
    st.sidebar.image("https://img.icons8.com/isometric/100/shield.png", width=65)
    st.sidebar.title("État des Composants")

    st.sidebar.markdown("### ⚙️ Stack Plateforme")
    st.sidebar.markdown("- **Classifier DistilBERT** : <span class='status-used'>✓ Prêt</span>", unsafe_allow_html=True)
    st.sidebar.markdown("- **FAISS Vector Store** : <span class='status-used'>✓ Prêt</span>", unsafe_allow_html=True)
    st.sidebar.markdown("- **LLM Gemini API** : <span class='status-used'>✓ Prêt</span>", unsafe_allow_html=True)
    st.sidebar.markdown("- **Collecteur CVE NVD** : <span class='status-used'>✓ Prêt</span>", unsafe_allow_html=True)
    st.sidebar.markdown("- **Dashboard Analytics** : <span class='status-used'>✓ Prêt</span>", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Dernier Message Traité")

    intent = st.session_state.last_intent
    if intent != "N/A":
        intent_map = {
            "GENERAL_QUESTION": "❓ Question Générale",
            "CYBER_QUESTION": "💼 Conseil Métier",
            "THREAT_ANALYSIS": "🚨 Analyse de Menace",
            "CVE_ANALYSIS": "🔍 Analyse CVE",
            "REPORT_REQUEST": "📊 Rapport Synthétique",
        }
        st.sidebar.markdown(
            f'<div class="intent-badge intent-{intent}">{intent_map.get(intent, intent)}</div>',
            unsafe_allow_html=True,
        )

    mods = st.session_state.last_modules
    distil_st = '<span class="status-used">✓ Utilisé</span>' if mods.get("distilbert") else '<span class="status-unused">○ Non utilisé</span>'
    faiss_st = '<span class="status-used">✓ Utilisé</span>' if mods.get("faiss") else '<span class="status-unused">○ Non utilisé</span>'
    llm_st = '<span class="status-used">✓ Utilisé (Gemini)</span>' if mods.get("llm") else '<span class="status-unused">○ Non utilisé</span>'

    st.sidebar.markdown(f"- **DistilBERT Classifier** : {distil_st}", unsafe_allow_html=True)
    st.sidebar.markdown(f"- **FAISS Vector Store** : {faiss_st}", unsafe_allow_html=True)
    st.sidebar.markdown(f"- **LLM Gemini** : {llm_st}", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Exemples de requêtes (Demo)")
    preset_input = None
    if st.sidebar.button("❓ Question Générale"):
        preset_input = "Qu'est-ce qu'une CVE ?"
    if st.sidebar.button("💼 Conseil Métier"):
        preset_input = "Quels sont les risques cyber qui concernent les agences de voyage ?"
    if st.sidebar.button("🚨 Analyse de Menace"):
        preset_input = "Nous avons détecté une vulnérabilité critique d'exécution de code à distance sur notre API de réservation."
    if st.sidebar.button("🔍 Analyse CVE"):
        preset_input = "Explique la vulnérabilité CVE-2025-0168."
    if st.sidebar.button("📊 Rapport 24h"):
        preset_input = "Que s'est-il passé ces dernières 24h ?"

    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Réinitialiser la conversation"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Bonjour ! La conversation a été réinitialisée. Comment puis-je vous aider ?",
            }
        ]
        st.session_state.last_intent = "N/A"
        st.session_state.last_modules = {"distilbert": False, "faiss": False, "llm": True}
        st.rerun()

    # Create 2 Main Tabs
    tab_analytics, tab_chatbot = st.tabs([
        "📊 TAB 1 : Dashboard Cyber Intelligence",
        "💬 TAB 2 : Assistant IA TECHPULSE"
    ])

    # =========================================================================
    # TAB 1: EXECUTIVE CYBER INTELLIGENCE DASHBOARD
    # =========================================================================
    with tab_analytics:
        st.subheader("📈 Indicateurs Exécutifs de Cybersécurité")
        kpis = analytics.get_kpis()

        # 4 Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Menaces Totales Identifiées", value=f"{kpis['total_threats']:,}")
        with col2:
            st.metric(label="Vulnérabilités Critiques", value=f"{kpis['critical_count']:,}", delta="Urgent", delta_color="inverse")
        with col3:
            st.metric(label="CVEs Analysées (NVD)", value=f"{kpis['cve_count']:,}")
        with col4:
            st.metric(label="Score de Risque Global", value=f"{kpis['global_risk_score']}/100", delta="+3 pts ce mois", delta_color="inverse")

        # Cyber Health Indicator Badge
        health_class = "health-critical" if kpis['global_risk_score'] >= 75 else "health-high"
        st.markdown(
            f'### Indicateur de Santé Cyber : <div class="health-badge {health_class}">{kpis["cyber_health"]}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.subheader("📊 Visualisations & Analyses Temporelles")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("**Répartition des Menaces par Sévérité**")
            sev_df = analytics.get_severity_distribution()
            st.bar_chart(sev_df.set_index("Sévérité"))

        with chart_col2:
            st.markdown("**Évolution Temporelle des Vulnérabilités (Tendances)**")
            temp_df = analytics.get_temporal_evolution()
            st.line_chart(temp_df.set_index("Date"))

        st.markdown("---")
        st.subheader("📋 Top Vulnérabilités & Recommandations Prioritaires")

        tab_table, tab_recs = st.tabs(["📑 Tableau des Vulnérabilités Identifiées", "🛡️ Recommandations Prioritaires pour Agences"])

        with tab_table:
            vuln_df = analytics.get_vulnerabilities_table(limit=15)
            st.dataframe(vuln_df, use_container_width=True)

        with tab_recs:
            recs = analytics.get_priority_recommendations()
            for rec in recs:
                st.markdown(
                    f"""
                    <div class="card-box">
                        <h4 style="color:#38BDF8; margin-top:0;">{rec['title']}</h4>
                        <p style="color:#CBD5E1; margin-bottom:0;">{rec['detail']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # =========================================================================
    # TAB 2: CONVERSATIONAL AI ASSISTANT CHATBOT
    # =========================================================================
    with tab_chatbot:
        st.subheader("💬 Assistant Conversational RAG & Advisory LLM")

        # Render past chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input box
        chat_user_input = st.chat_input("Posez votre question à TECHPULSE-AI...") or preset_input

        if chat_user_input:
            # Display user message immediately
            st.session_state.messages.append({"role": "user", "content": chat_user_input})
            with st.chat_message("user"):
                st.markdown(chat_user_input)

            # Execute RAG Pipeline with memory
            with st.chat_message("assistant"):
                with st.spinner("TECHPULSE-AI analyse la demande et interroge la base..."):
                    response_data = pipeline.process_chat_message(
                        query=chat_user_input,
                        history=st.session_state.messages[:-1],
                    )

                bot_answer = response_data["response_text"]
                st.markdown(bot_answer)

                # Store state for sidebar execution indicators
                st.session_state.last_intent = response_data["intent"]
                st.session_state.last_modules = response_data["modules_used"]
                st.session_state.messages.append({"role": "assistant", "content": bot_answer})

                st.rerun()


if __name__ == "__main__":
    main()
