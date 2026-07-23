"""
TECHPULSE-AI — LLM Integration Layer (Gemini / OpenAI / Offline Template)
==========================================================================
Generates natural, human-sounding responses for the 4 decision matrix categories.

Decision Matrix Categories:
    1. GENERAL_CONVERSATION → Greetings, friendly chat, system status (NO CVEs, NO emergency tone)
    2. PREVENTIVE_SECURITY  → Best practice guides for Amadeus/Sabre APIs, PCI-DSS, CVE definitions (NO emergency tone)
    3. CYBER_INCIDENT       → Active attacks, RCE, ransomware, specific CVE flaws (Emergency protocol & remediation)
    4. GLOBAL_REPORT        → Executive 24h activity summaries

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
# System Prompts per Decision Matrix Category
# ---------------------------------------------------------------------------

_SYSTEM_GENERAL = """\
Tu es TECHPULSE-AI, un assistant virtuel expert en cybersécurité pour le secteur du voyage.
Réponds de manière amicale, courte, fluide et naturelle.
INTERDICTIONS STRICTES :
- Ne cite AUCUNE CVE.
- Ne parle PAS d'isolation de serveur, de blocage WAF d'urgence ou d'attaque.
- Ne fais référence à aucune fausse menace.
"""

_SYSTEM_PREVENTIVE = """\
Tu es TECHPULSE-AI, expert en architecture et sécurité préventive pour le secteur du voyage.
Fournis un guide clair et structuré de bonnes pratiques techniques (ex: OAuth 2.0 avec jetons de courte durée, mTLS bi-directionnel, Rate Limiting strict, chiffrement des données PNR/passeports, audit des logs, conformité PCI-DSS).
INTERDICTIONS STRICTES :
- N'utilise PAS un ton d'incident d'urgence (PAS de "Serveur isolé d'urgence", PAS de "Attaque détectée").
- Ne cite de CVE QUE SI l'utilisateur a explicitement mentionné un identifiant CVE spécifique.
"""

_SYSTEM_INCIDENT = """\
Tu es TECHPULSE-AI, coordinateur d'urgence en cybersécurité pour le secteur du voyage.
L'utilisateur signale une alerte, une attaque active (ransomware, RCE, fuite de données) ou une vulnérabilité critique.
Déclenche immédiatement le protocole d'urgence avec un plan d'action de remédiation (Isolation réseau, filtrage WAF strict, révocation des clés API GDS, déploiement de patchs).
"""

_SYSTEM_REPORT = """\
Tu es TECHPULSE-AI, analyste senior en cybersécurité pour le secteur du voyage.
À partir des métriques et données fournies, rédige une synthèse exécutive fluide, claire et professionnelle des dernières 24h pour la direction des agences de voyage.
"""


class LLMGenerator:
    """
    Large Language Model integration supporting Gemini, OpenAI, and Offline fallback.
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

    def _init_client(self) -> None:
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

        LOGGER.info("No active LLM API key — offline template engine will be used.")

    @staticmethod
    def extract_valid_cves(matches: List[Dict[str, Any]]) -> List[str]:
        """Strictly extracts only valid CVE identifiers (e.g. CVE-2025-0168)."""
        pattern = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)
        valid = []
        if not matches:
            return valid
        for m in matches:
            raw_id = str(m.get("id") or m.get("cve_id") or m.get("record_id") or "").strip().upper()
            if pattern.match(raw_id) and raw_id not in valid:
                valid.append(raw_id)
        return valid

    def generate_advisory(
        self,
        query: str,
        intent: str = "PREVENTIVE_SECURITY",
        severity: Optional[str] = None,
        confidence: Optional[float] = None,
        retrieved_matches: Optional[List[Dict[str, Any]]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        system_metrics: Optional[Dict[str, Any]] = None,
    ) -> str:
        prompt = self._build_prompt(
            query=query,
            intent=intent,
            severity=severity,
            confidence=confidence,
            retrieved_matches=retrieved_matches or [],
            history=history or [],
            system_metrics=system_metrics or {},
        )

        if self.active_provider == "gemini":
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                return response.text
            except Exception as err:
                LOGGER.error("Gemini API error: %s", err)

        if self.active_provider == "openai":
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content or ""
            except Exception as err:
                LOGGER.error("OpenAI API error: %s", err)

        return self._offline_response(
            query=query,
            intent=intent,
            severity=severity,
            matches=retrieved_matches or [],
            system_metrics=system_metrics or {},
        )

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
        history_block = self._format_history(history)
        metrics_block = self._format_metrics(system_metrics)
        
        valid_cves = self.extract_valid_cves(retrieved_matches)
        context_block = self._format_matches(retrieved_matches) if valid_cves else ""

        if intent == "GENERAL_CONVERSATION":
            parts = [_SYSTEM_GENERAL, ""]
            if metrics_block:
                parts += [f"État du système :\n{metrics_block}", ""]
            parts.append(f"Question : {query}")
            return "\n".join(parts)

        elif intent == "PREVENTIVE_SECURITY":
            parts = [_SYSTEM_PREVENTIVE, ""]
            if context_block:
                parts += [f"Vulnérabilités de référence (si pertinentes) :\n{context_block}", ""]
            parts.append(f"Demande : {query}")
            return "\n".join(parts)

        elif intent == "CYBER_INCIDENT":
            parts = [_SYSTEM_INCIDENT, ""]
            if context_block:
                parts += [f"Failles identifiées (base FAISS) :\n{context_block}", ""]
            if severity:
                parts += [f"Sévérité estimée : {severity}", ""]
            parts.append(f"Alerte / Question : {query}")
            return "\n".join(parts)

        else:  # GLOBAL_REPORT
            parts = [_SYSTEM_REPORT, "", f"Données réelles :\n{metrics_block or '(N/A)'}", ""]
            parts.append(f"Demande : {query}")
            return "\n".join(parts)

    def _offline_response(
        self,
        query: str,
        intent: str,
        severity: Optional[str],
        matches: List[Dict[str, Any]],
        system_metrics: Dict[str, Any],
    ) -> str:
        q = query.lower()

        # CAS 1 : Conversation Générale / État Système / Greetings
        if intent == "GENERAL_CONVERSATION":
            if any(k in q for k in ["bilan", "état", "etat", "statut", "fonctionne", "opérationnel"]):
                metrics_block = self._format_metrics(system_metrics)
                return (
                    "Voici l'état actuel de la plateforme **TECHPULSE-AI** :\n\n"
                    + (metrics_block.replace("  •", "-") if metrics_block else
                       "- **Moteur Analytics** : 🟢 Actif\n- **Base de Connaissances GDS** : 🟢 En ligne\n- **Système de Détection** : 🟢 Operationnel\n")
                    + "\nTous les services de sécurité pour les agences de voyage fonctionnent normalement."
                )

            return (
                "Bonjour ! Je suis **TECHPULSE-AI**, votre assistant virtuel en cybersécurité pour le secteur du voyage. 👋\n\n"
                "Comment puis-je vous aider aujourd'hui ? (ex: *sécurisation des API GDS Amadeus*, *bonnes pratiques PCI-DSS*, *analyse d'une vulnérabilité*)"
            )

        # CAS 2 : Sécurisation Préventive & Architecture
        elif intent == "PREVENTIVE_SECURITY":
            if "cve" in q and ("qu'est-ce" in q or "c'est quoi" in q or "définition" in q):
                return (
                    "Une **CVE** (*Common Vulnerabilities and Exposures*) est un identifiant universel attribué aux vulnérabilités de sécurité connues.\n\n"
                    "Dans le secteur du tourisme et des agences de voyage, le suivi des CVE permet de maintenir vos serveurs de réservation et connecteurs GDS (Amadeus, Sabre) à jour avant l'émergence d'exploits."
                )

            return (
                "Pour sécuriser les intégrations et API de réservation de votre agence de voyage (Amadeus, Sabre, Galileo) :\n\n"
                "1. **Authentification & Muting Token** : Utilisez des jetons OAuth 2.0 à durée de vie courte (15 minutes max).\n"
                "2. **Mutual TLS (mTLS)** : Exigez des certificats bi-directionnels pour sécuriser l'ensemble des webhooks GDS.\n"
                "3. **Rate Limiting Stricte** : Limitez le nombre de requêtes par minute pour empêcher la collecte automatisée de tarifs et d'inventaires.\n"
                "4. **Audit Centralisé & PCI-DSS** : Chiffrez les données de paiement et les PNR voyageurs au repos et en transit."
            )

        # CAS 3 : Incident / Attaque / Faille Spécifique (Urgence)
        elif intent == "CYBER_INCIDENT":
            valid_cves = self.extract_valid_cves(matches)
            cve_ref = f" (référencée dans {valid_cves[0]})" if valid_cves else ""

            return (
                f"🚨 **Alerte d'Analyse de Menace Critique**{cve_ref}\n\n"
                "Une vulnérabilité ou attaque active a été identifiée sur vos systèmes de réservation. Risque majeur de prise de contrôle et d'exfiltration de données voyageurs.\n\n"
                "**Plan d'Action Immédiat :**\n"
                "- **Isolation Réseau** : Isolez la machine hôte et placez le serveur derrière un WAF en mode blocage strict.\n"
                "- **Révocation des Identifiants** : Réinitialisez immédiatement toutes les clés d'API et jetons d'accès GDS.\n"
                "- **Patching d'Urgence** : Appliquez les correctifs de sécurité éditeur sans délai."
            )

        # CAS 4 : Rapport Global / Bilan 24h
        else:
            metrics = system_metrics or {}
            return (
                f"**Rapport d'Intelligence Cyber — Synthèse 24h** 🛡️\n\n"
                f"**Bilan de Santé :** La plateforme a supervisé **{metrics.get('total_threats', '142')} événements**, "
                f"dont **{metrics.get('critical_count', '3')} alertes critiques**. "
                f"Le score de risque global est évalué à **{metrics.get('global_risk_score', '24')}/100**.\n\n"
                "**Recommandations Exécutives :**\n"
                "- Poursuivre la surveillance des connecteurs billetterie.\n"
                "- Vérifier le renouvellement des certificats SSL/TLS sur les passerelles de paiement.\n"
                "- Effectuer un audit hebdomadaire des droits d'accès API."
            )

    @staticmethod
    def _format_history(history: List[Dict[str, str]]) -> str:
        if not history:
            return ""
        lines = []
        for m in history[-4:]:
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
            f"  • Score de risque global : {metrics.get('global_risk_score', 'N/A')}/100\n"
            f"  • État : {metrics.get('cyber_health', 'Opérationnel')}"
        )

    @staticmethod
    def _format_matches(matches: List[Dict[str, Any]]) -> str:
        if not matches:
            return ""
        lines = []
        for m in matches[:5]:
            cve_id   = m.get("id") or m.get("cve_id") or m.get("record_id", "")
            if not cve_id or not str(cve_id).startswith("CVE-"):
                continue
            severity = m.get("severity", "N/A")
            desc     = str(m.get("description", ""))[:200]
            lines.append(f"  • [{cve_id}] {severity} | {desc}")
        return "\n".join(lines)
