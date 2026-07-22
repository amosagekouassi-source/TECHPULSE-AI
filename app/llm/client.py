"""
TECHPULSE-AI — LLM Integration Layer (Gemini / OpenAI / Offline Template)
==========================================================================
Generates natural, human-sounding French responses for the 3 intent categories.

System Prompts Philosophy:
    - No rigid section headers ("1. Résumé", "2. Impact", etc.)
    - LLM formats the answer organically like a knowledgeable human expert
    - Each intent gets its own minimal, purposeful system prompt

Author: TECHPULSE-AI Engineering
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()
LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System Prompts — one per intent, clean and non-prescriptive
# ---------------------------------------------------------------------------

_SYSTEM_GENERAL = """\
Tu es TECHPULSE-AI, un assistant virtuel expert en cybersécurité pour le secteur du voyage.
Réponds de manière naturelle, fluide et chaleureuse — comme un collègue expert qui discute.
N'impose pas de structure de rapport. Si la question est une simple salutation ou question \
générale, réponds poliment et simplement sans citer de CVE ou de métriques de sécurité inutiles.\
"""

_SYSTEM_REPORT = """\
Tu es TECHPULSE-AI, analyste en cybersécurité spécialisé dans le secteur du voyage et du tourisme.
À partir des métriques et des vulnérabilités ci-dessous, rédige un rapport exécutif \
synthétique, clair et lisible pour un directeur d'agence de voyage.
Sois concis, percutant et factuel. Évite le jargon technique excessif. \
Ne génère pas de numéros de section rigides.\
"""

_SYSTEM_CYBER = """\
Tu es TECHPULSE-AI, expert en cybersécurité pour le secteur du voyage et du tourisme.
À partir de la question et du contexte de vulnérabilités fourni, génère une analyse \
de sécurité précise, naturelle et pédagogue.
Adapte le niveau de détail technique à la question. Si c'est une question de définition \
(ex: "Qu'est-ce qu'une CVE ?"), réponds simplement et clairement sans imposer de métriques.
Si c'est une alerte ou une analyse de menace spécifique, donne des recommandations concrètes \
de remédiation de façon fluide, sans numéros de section systématiques.\
"""


class LLMGenerator:
    """
    Large Language Model integration for TECHPULSE-AI.

    Supported providers (auto-detected in order):
        1. Gemini (google-genai SDK) — if GEMINI_API_KEY or GOOGLE_API_KEY set
        2. OpenAI                    — if OPENAI_API_KEY set
        3. Offline template engine   — graceful degradation, no API required
    """

    def __init__(
        self,
        provider: str = "auto",
        model_name: Optional[str] = None,
    ) -> None:
        self.provider = provider.lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
        self._init_client()

    # -----------------------------------------------------------------------
    # Initialisation
    # -----------------------------------------------------------------------

    def _init_client(self) -> None:
        """Resolve and initialise the active LLM backend."""
        self.active_provider = "template"

        if self.provider in ("auto", "gemini") and self.gemini_api_key:
            try:
                import google.genai as genai
                self.client = genai.Client(api_key=self.gemini_api_key)
                self.active_provider = "gemini"
                self.model_name = self.model_name or "gemini-2.0-flash"
                LOGGER.info("Gemini LLM initialised — model: %s", self.model_name)
                return
            except Exception as err:
                LOGGER.warning("Gemini initialisation failed: %s", err)

        if self.provider in ("auto", "openai") and self.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_api_key)
                self.active_provider = "openai"
                self.model_name = self.model_name or "gpt-4o-mini"
                LOGGER.info("OpenAI LLM initialised — model: %s", self.model_name)
                return
            except Exception as err:
                LOGGER.warning("OpenAI initialisation failed: %s", err)

        LOGGER.info("No LLM API key found — offline template engine will be used.")

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def generate_advisory(
        self,
        query: str,
        intent: str = "CYBER_THREAT",
        severity: Optional[str] = None,
        confidence: Optional[float] = None,
        retrieved_matches: Optional[List[Dict[str, Any]]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        system_metrics: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a contextual, natural-language response from the LLM.

        Args:
            query:             The user's original question.
            intent:            One of "GENERAL_CONVERSATION", "GLOBAL_REPORT", "CYBER_THREAT".
            severity:          DistilBERT severity label (CYBER_THREAT only).
            confidence:        DistilBERT confidence score.
            retrieved_matches: FAISS semantic search results.
            history:           Recent conversation turns.
            system_metrics:    Live platform KPIs (GLOBAL_REPORT / GENERAL_CONVERSATION).

        Returns:
            Human-readable Markdown response string.
        """
        prompt = self._build_prompt(
            query=query,
            intent=intent,
            severity=severity,
            confidence=confidence,
            retrieved_matches=retrieved_matches or [],
            history=history or [],
            system_metrics=system_metrics or {},
        )

        # Try Gemini
        if self.active_provider == "gemini":
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                return response.text
            except Exception as err:
                LOGGER.error("Gemini API error: %s", err, exc_info=True)
                LOGGER.warning("Falling back to offline template engine.")

        # Try OpenAI
        if self.active_provider == "openai":
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content or ""
            except Exception as err:
                LOGGER.error("OpenAI API error: %s", err, exc_info=True)
                LOGGER.warning("Falling back to offline template engine.")

        # Offline template engine (no API required)
        return self._offline_response(
            query=query,
            intent=intent,
            severity=severity,
            matches=retrieved_matches or [],
            system_metrics=system_metrics or {},
        )

    # -----------------------------------------------------------------------
    # Prompt Builder — clean, non-prescriptive structure
    # -----------------------------------------------------------------------

    def _build_prompt(
        self,
        query: str,
        intent: str,
        severity: Optional[str],
        confidence: Optional[float],
        retrieved_matches: List[Dict[str, Any]],
        history: List[Dict[str, str]],
        system_metrics: Dict[str, Any],
    ) -> str:
        """Build a context-rich prompt tailored to the detected intent."""

        history_block = self._format_history(history)
        metrics_block = self._format_metrics(system_metrics)
        context_block = self._format_matches(retrieved_matches)

        if intent == "GENERAL_CONVERSATION":
            parts = [
                _SYSTEM_GENERAL,
                "",
            ]
            if metrics_block:
                parts += [f"État du système :\n{metrics_block}", ""]
            if history_block:
                parts += [f"Historique récent :\n{history_block}", ""]
            parts.append(f"Question : {query}")
            return "\n".join(parts)

        elif intent == "GLOBAL_REPORT":
            parts = [
                _SYSTEM_REPORT,
                "",
                f"Métriques temps réel :\n{metrics_block or '(non disponibles)'}",
                "",
            ]
            if context_block:
                parts += [f"Top vulnérabilités récentes :\n{context_block}", ""]
            if history_block:
                parts += [f"Contexte conversationnel :\n{history_block}", ""]
            parts.append(f"Demande : {query}")
            return "\n".join(parts)

        else:  # CYBER_THREAT
            parts = [
                _SYSTEM_CYBER,
                "",
            ]
            if context_block:
                parts += [f"Contexte de vulnérabilités (base FAISS) :\n{context_block}", ""]
            if severity and confidence is not None:
                parts += [
                    f"Sévérité estimée (DistilBERT) : {severity} "
                    f"(confiance : {confidence * 100:.0f}%)",
                    "",
                ]
            if history_block:
                parts += [f"Historique récent :\n{history_block}", ""]
            parts.append(f"Question : {query}")
            return "\n".join(parts)

    # -----------------------------------------------------------------------
    # Formatting helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _format_history(history: List[Dict[str, str]]) -> str:
        if not history:
            return ""
        recent = history[-4:]  # last 2 turns
        lines = []
        for m in recent:
            role = m.get("role", "user").capitalize()
            content = m.get("content", "")
            lines.append(f"  {role}: {content}")
        return "\n".join(lines)

    @staticmethod
    def _format_metrics(metrics: Dict[str, Any]) -> str:
        if not metrics:
            return ""
        return (
            f"  • Menaces répertoriées : {metrics.get('total_threats', 'N/A')}\n"
            f"  • Vulnérabilités critiques : {metrics.get('critical_count', 'N/A')}\n"
            f"  • CVE indexées : {metrics.get('cve_count', 'N/A')}\n"
            f"  • Score de risque global : {metrics.get('global_risk_score', 'N/A')}/100\n"
            f"  • État : {metrics.get('cyber_health', 'Opérationnel')}"
        )

    @staticmethod
    def _format_matches(matches: List[Dict[str, Any]]) -> str:
        if not matches:
            return ""
        lines = []
        for m in matches[:5]:
            cve_id   = m.get("id") or m.get("record_id", "CVE")
            score    = m.get("similarity_score", 0.0)
            severity = m.get("severity", "N/A")
            desc     = str(m.get("description", ""))[:200]
            lines.append(f"  • [{cve_id}] score={score:.2f} | {severity} | {desc}")
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Offline response engine (no API key required)
    # -----------------------------------------------------------------------

    def _offline_response(
        self,
        query: str,
        intent: str,
        severity: Optional[str],
        matches: List[Dict[str, Any]],
        system_metrics: Dict[str, Any],
    ) -> str:
        """
        Offline template engine — rich but honest, no fake CVE responses.
        Used when no LLM API key is configured.
        """
        q = query.lower()

        if intent == "GENERAL_CONVERSATION":
            # Greeting
            greetings = ["bonjour", "salut", "hello", "coucou", "bonsoir", "hey", "hi"]
            if any(re.search(rf"\b{g}\b", q) for g in greetings):
                return (
                    "Bonjour ! Je suis **TECHPULSE-AI**, votre assistant en cybersécurité "
                    "pour le secteur du voyage. 👋\n\n"
                    "Je peux vous aider à analyser des menaces cyber, vous expliquer des CVE, "
                    "sécuriser vos API de réservation, ou générer un rapport d'activité 24h.\n\n"
                    "*Que puis-je faire pour vous ?*"
                )

            # System status
            if any(k in q for k in ["bilan", "état", "etat", "statut", "fonctionne", "opérationnel"]):
                metrics_block = self._format_metrics(system_metrics)
                return (
                    "Voici l'état actuel de la plateforme **TECHPULSE-AI** :\n\n"
                    + (metrics_block.replace("  •", "-") if metrics_block else
                       "- **Classificateur DistilBERT** : 🟢 Actif\n"
                       "- **Index FAISS** : 🟢 Actif\n"
                       "- **LLM (mode template)** : 🟡 Offline\n"
                       "- **Moteur Analytics** : 🟢 Actif\n")
                    + "\nTous les composants d'intelligence cyber sont opérationnels."
                )

            # Definition queries
            if any(k in q for k in ["qu'est-ce", "c'est quoi", "définition", "expliqu"]):
                if "cve" in q:
                    return (
                        "Une **CVE** (*Common Vulnerabilities and Exposures*) est un identifiant unique "
                        "attribué à une vulnérabilité de sécurité connue et publiée.\n\n"
                        "Dans le secteur du voyage, les équipes IT utilisent les CVE pour suivre "
                        "précisément les failles affectant leurs serveurs web, passerelles de paiement "
                        "et API GDS (Amadeus, Sabre, Travelport) — et déployer les correctifs avant "
                        "qu'un attaquant ne les exploite."
                    )
                return (
                    f"Bonne question ! Pour répondre à *\"{query}\"*, je serais plus précis "
                    "si vous pouvez reformuler avec un terme technique spécifique "
                    "(CVE, attaque, protocole, outil de sécurité...).\n\n"
                    "Je suis là pour vous aider !"
                )

            return (
                f"Je suis TECHPULSE-AI, votre assistant cybersécurité pour le voyage. "
                f"Pour votre question sur *\"{query}\"*, n'hésitez pas à me donner plus de contexte — "
                "je pourrai ainsi vous fournir une réponse plus précise et utile."
            )

        elif intent == "GLOBAL_REPORT":
            metrics = system_metrics or {}
            cves_str = ", ".join(
                str(m.get("id", "CVE")) for m in matches[:3]
            ) if matches else "aucune CVE critique remontée"

            return (
                f"**Rapport d'Intelligence Cyber — Dernières 24h** 🛡️\n\n"
                f"**Résumé exécutif :** La plateforme a traité "
                f"**{metrics.get('total_threats', 'N/D')} menaces** au total, dont "
                f"**{metrics.get('critical_count', 'N/D')} critiques**. "
                f"Le score de risque global s'établit à **{metrics.get('global_risk_score', 'N/D')}/100** "
                f"— état : *{metrics.get('cyber_health', 'Surveillance continue')}*.\n\n"
                f"**Vulnérabilités prioritaires :** {cves_str}.\n\n"
                "**Recommandations immédiates :**\n"
                "- Auditer les accès API de réservation pour détecter toute activité anormale\n"
                "- Vérifier la conformité PCI-DSS des flux de paiement\n"
                "- Appliquer les correctifs disponibles sur les systèmes exposés\n\n"
                "*Pour une analyse détaillée d'une menace spécifique, posez-moi la question directement.*"
            )

        else:  # CYBER_THREAT
            cves_info = (
                f" (sources : {', '.join(str(m.get('id', 'CVE')) for m in matches[:3])})"
                if matches else ""
            )
            sev_info = f" — sévérité estimée : **{severity}**" if severity else ""

            return (
                f"J'ai analysé votre question sur *\"{query}\"*{sev_info}.\n\n"
                f"Ce type de menace peut impacter directement vos API de réservation, "
                f"vos passerelles de paiement et les données personnelles de vos voyageurs. "
                f"Voici les axes de remédiation prioritaires :\n\n"
                f"- **Isolation** : Identifiez et isolez le service ou composant vulnérable\n"
                f"- **Filtrage WAF** : Appliquez une règle de blocage au niveau du pare-feu applicatif\n"
                f"- **Mise à jour** : Déployez le correctif éditeur dès sa disponibilité{cves_info}\n"
                f"- **Audit de logs** : Vérifiez les journaux d'accès pour détecter toute exploitation\n\n"
                "Avez-vous besoin d'une analyse plus approfondie ou d'un modèle d'alerte pour vos équipes ?"
            )

    @staticmethod
    def _polite_error_message() -> str:
        """Return a clean user-facing error message when the LLM API fails."""
        return (
            "Je rencontre actuellement une difficulté à contacter le service de génération de réponses. "
            "Merci de réessayer dans un instant. "
            "Si le problème persiste, vérifiez la validité de votre clé API Gemini."
        )
