"""LLM integration layer for TECHPULSE-AI (Gemini / OpenAI / Fallback)."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

LOGGER = logging.getLogger(__name__)

TECHPULSE_SYSTEM_PROMPT = """Tu es TECHPULSE-AI, un assistant cybersécurité spécialisé dans les agences de voyage.

Tu aides les responsables informatiques, dirigeants et équipes métiers à comprendre les vulnérabilités, cyberattaques, risques de fraude, menaces sur les systèmes de réservation, plateformes de billetterie, solutions de paiement et données clients.

Tu expliques les risques avec un langage clair tout en conservant la précision technique.

Tu fournis des recommandations concrètes et adaptées au secteur du voyage."""


class LLMGenerator:
    """Large Language Model generator for cybersecurity conversational advisories."""

    def __init__(
        self,
        provider: str = "auto",
        model_name: Optional[str] = None,
    ) -> None:
        """Initialize LLM provider client.

        Args:
            provider: 'auto', 'gemini', 'openai', or 'template'.
            model_name: Model identifier (e.g., 'gemini-2.5-flash', 'gpt-4o-mini').
        """
        self.provider = provider.lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = model_name

        self._init_client()

    def _init_client(self) -> None:
        """Resolve and initialize active LLM SDK."""
        self.active_provider = "template"

        if self.provider in ("auto", "gemini") and self.gemini_api_key:
            try:
                import google.genai as genai
                self.client = genai.Client(api_key=self.gemini_api_key)
                self.active_provider = "gemini"
                self.model_name = self.model_name or "gemini-2.5-flash"
                LOGGER.info("Initialized Gemini LLM provider with model %s", self.model_name)
                return
            except Exception as err:
                LOGGER.warning("Could not initialize google.genai: %s", err)

        if self.provider in ("auto", "openai") and self.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_api_key)
                self.active_provider = "openai"
                self.model_name = self.model_name or "gpt-4o-mini"
                LOGGER.info("Initialized OpenAI LLM provider with model %s", self.model_name)
                return
            except Exception as err:
                LOGGER.warning("Could not initialize OpenAI client: %s", err)

        LOGGER.info("No active LLM API key detected; using offline Cybersecurity Advisor engine.")

    def generate_advisory(
        self,
        query: str,
        intent: str = "THREAT_ANALYSIS",
        severity: Optional[str] = None,
        confidence: Optional[float] = None,
        retrieved_matches: Optional[List[Dict[str, Any]]] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Generate a structured conversational cybersecurity response.

        Args:
            query: User input query.
            intent: Detected intent ('THREAT_ANALYSIS', 'BUSINESS_ADVICE', 'GENERAL').
            severity: Predicted DistilBERT severity if applicable.
            confidence: Severity confidence score if applicable.
            retrieved_matches: FAISS matches if applicable.
            history: Conversation history list.

        Returns:
            Structured Markdown response.
        """
        matches = retrieved_matches or []
        history_str = ""
        if history:
            recent = history[-4:]  # Last 2 turns
            history_str = "\n".join(
                f"- {m.get('role', 'user').capitalize()}: {m.get('content', '')}"
                for m in recent
            )

        context_str = ""
        if matches:
            context_str = "\n".join(
                f"- [{m.get('id', 'CVE')}] Score: {m.get('similarity_score', 0):.2f} | Sévérité: {m.get('severity', 'N/A')} | {m.get('description', '')[:250]}"
                for m in matches[:3]
            )

        prompt = f"""{TECHPULSE_SYSTEM_PROMPT}

HISTORIQUE RÉCENT DE LA CONVERSATION :
{history_str or "Premier message de la session."}

QUESTION ACTUELLE DE L'UTILISATEUR :
"{query}"

INTENTION DÉTECTÉE : {intent}
"""
        if severity:
            prompt += f"ÉVALUATION DE SÉVÉRITÉ (DistilBERT) : {severity} (Confiance : {confidence * 100:.1f}%)\n"

        if context_str:
            prompt += f"SOURCES DE MENACES EXTRACTES DU RAG (FAISS) :\n{context_str}\n"

        prompt += """
STRUCTURE DE RÉPONSE OBLIGATOIRE EN FRANÇAIS :
1. **Résumé** (Explication claire et directe répondant à la question)
2. **Impact potentiel (Secteur Voyage)** (Impact sur plateformes de réservation, billetterie, API, cartes bancaires ou données voyageurs)
3. **Analyse technique** (Détail technique clair, CVEs pertinentes si applicables)
4. **Recommandations concrètes** (Plan d'action et mesures d'atténuation)
5. **Sources RAG utilisées** (Lister brièvement les identifiants CVE/incidents utilisés si applicables, ou mentionner "Aucune source externe nécessaire" pour les questions générales)
"""

        if self.active_provider == "gemini":
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                return response.text
            except Exception as err:
                LOGGER.error("Gemini generation error: %s", err)

        if self.active_provider == "openai":
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content or ""
            except Exception as err:
                LOGGER.error("OpenAI generation error: %s", err)

        # Offline template fallback
        return self._generate_offline_template(query, intent, severity, confidence, matches)

    def _generate_offline_template(
        self,
        query: str,
        intent: str,
        severity: Optional[str],
        confidence: Optional[float],
        matches: List[Dict[str, Any]],
    ) -> str:
        """Offline template synthesizer for Demo Day without external API calls."""
        cves = ", ".join([str(m.get("id") or "CVE") for m in matches[:3]]) if matches else "Aucune source RAG requise"
        sev_str = f"**{severity}** ({confidence * 100:.1f}%)" if severity else "Non applicable (Question générale)"

        return f"""### 🛡️ Réponse TECHPULSE-AI

#### 1. Résumé
Pour répondre à votre demande concernant *"{query}"*, le système a identifié la catégorie d'intention **{intent}**.

#### 2. Impact potentiel (Secteur Voyage)
- **Systèmes concernés** : Moteurs de réservation, API de billetterie et passerelles de paiement.
- **Évaluation de Sévérité** : {sev_str}

#### 3. Analyse technique
- Les requêtes et menaces associées ont été analysées via notre base de données spécialisée.
- {len(matches)} enregistrements pertinents ont été extraits par recherche vectorielle.

#### 4. Recommandations concrètes
1. Auditer les points d'entrée API et passerelles de paiement.
2. Déployer les règles de sécurité WAF appropriées et restreindre les jetons d'accès.
3. Planifier les mises à jour de sécurité nécessaires.

#### 5. Sources RAG utilisées
- Sources : `{cves}`
"""
