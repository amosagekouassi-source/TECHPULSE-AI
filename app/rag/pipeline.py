"""
TECHPULSE-AI — RAG Pipeline (Clean Architecture)
=================================================
Clean-slate implementation with a 3-intent routing architecture:

    GENERAL_CONVERSATION  →  Direct LLM call (no FAISS, no forced CVE context)
    GLOBAL_REPORT         →  Analytics metrics + LLM executive summary
    CYBER_THREAT          →  FAISS semantic search + LLM security advisory

Author: TECHPULSE-AI Engineering
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.analytics.engine import CyberAnalyticsEngine
from app.classifier.predict import SeverityPredictor
from app.llm.client import LLMGenerator
from app.reports.generator import ReportGenerator
from app.vector_store.faiss_store import FAISSVectorStore
from app.rag.intent_router import IntentRouter, Intent

LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pipeline Response TypedDict-style schema
# ---------------------------------------------------------------------------
# Every call to RAGPipeline.chat() returns a Dict with these guaranteed keys:
#
#   query           (str)  – The original user input
#   intent          (str)  – One of: "GENERAL_CONVERSATION", "GLOBAL_REPORT", "CYBER_THREAT"
#   response_text   (str)  – The final human-readable response from the LLM
#   modules_used    (dict) – Boolean flags for each subsystem that was invoked
#   matches         (list) – FAISS results (empty list if FAISS was not used)
#   severity        (str|None)  – DistilBERT predicted severity label
#   confidence      (float|None) – DistilBERT confidence score
#   llm_provider    (str)  – Active LLM backend ("gemini", "openai", "template")
# ---------------------------------------------------------------------------


class RAGPipeline:
    """
    Conditional RAG pipeline implementing a 3-intent execution strategy.

    Execution branches:
        - GENERAL_CONVERSATION: Direct LLM — friendly, conversational, no FAISS
        - GLOBAL_REPORT:        Analytics KPIs → LLM executive summary
        - CYBER_THREAT:         FAISS search → DistilBERT classification → LLM advisory
    """

    def __init__(
        self,
        model_reference: Optional[Path | str] = None,
        vector_store_dir: Path | str = Path("models/vector_store"),
        llm_provider: str = "auto",
    ) -> None:
        """Initialise all pipeline subsystems lazily with graceful degradation."""
        # Core components — always instantiated
        self.router = IntentRouter()
        self.llm = LLMGenerator(provider=llm_provider)
        self.analytics = CyberAnalyticsEngine()

        # Threat-specific components — FAISS + DistilBERT (optional/lazy)
        self.vector_store = FAISSVectorStore(index_dir=vector_store_dir)
        self.predictor: Optional[SeverityPredictor] = None

        model_path = Path(model_reference or "models/distilbert-severity")
        if model_path.is_dir():
            try:
                self.predictor = SeverityPredictor(model_reference=model_path)
                LOGGER.info("DistilBERT severity predictor loaded from %s", model_path)
            except Exception as err:
                LOGGER.warning("DistilBERT model unavailable — severity scoring disabled: %s", err)

        # Report generator wraps analytics + llm
        self.reports = ReportGenerator(
            analytics_engine=self.analytics,
            llm_generator=self.llm,
        )

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Process a user message through the 3-intent routing pipeline.

        Args:
            message:  Raw user input string.
            history:  Conversation history as list of {"role": ..., "content": ...} dicts.
            top_k:    Number of FAISS nearest-neighbour matches to retrieve (CYBER_THREAT only).

        Returns:
            Response payload dict. See module docstring for schema.
        """
        text = message.strip()
        if not text:
            return self._error_response(
                query="",
                intent=Intent.GENERAL_CONVERSATION,
                message="Le message ne peut pas être vide.",
            )

        intent = self.router.classify(text)
        LOGGER.info("Intent classified as '%s' for input: %.80s", intent.value, text)

        try:
            if intent == Intent.GENERAL_CONVERSATION:
                return self._handle_general(text, history)
            elif intent == Intent.GLOBAL_REPORT:
                return self._handle_report(text, history)
            else:  # Intent.CYBER_THREAT
                return self._handle_cyber_threat(text, history, top_k)
        except Exception as err:
            LOGGER.error(
                "Unhandled pipeline error [intent=%s, query='%.80s']: %s",
                intent.value, text, err, exc_info=True,
            )
            return self._error_response(
                query=text,
                intent=intent,
                message=(
                    "Une erreur inattendue s'est produite. Nos équipes techniques ont été notifiées. "
                    "Merci de réessayer dans un instant."
                ),
            )

    def process_chat_message(
        self,
        query: Optional[str] = None,
        message: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Backwards-compatible alias mapping legacy kwargs to chat()."""
        user_input = query or message or ""
        return self.chat(message=user_input, history=history, top_k=top_k)

    def process_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Legacy single-query wrapper. Adds 'advisory' alias to response."""
        result = self.chat(message=query, history=None, top_k=top_k)
        result["advisory"] = result["response_text"]
        return result

    # -----------------------------------------------------------------------
    # Private Execution Branches
    # -----------------------------------------------------------------------

    def _handle_general(
        self,
        text: str,
        history: Optional[List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        """
        Branch A — GENERAL_CONVERSATION.
        Sends the query directly to Gemini with a conversational system prompt.
        FAISS is NOT queried. No CVE context is forced.
        """
        system_metrics: Optional[Dict[str, Any]] = None
        try:
            system_metrics = self.analytics.get_kpis()
        except Exception as err:
            LOGGER.warning("Could not retrieve analytics KPIs for general query: %s", err)

        response_text = self.llm.generate_advisory(
            query=text,
            intent=Intent.GENERAL_CONVERSATION.value,
            history=history,
            system_metrics=system_metrics,
        )

        return {
            "query": text,
            "intent": Intent.GENERAL_CONVERSATION.value,
            "response_text": response_text,
            "modules_used": {"faiss": False, "distilbert": False, "llm": True, "analytics": True},
            "matches": [],
            "severity": None,
            "confidence": None,
            "llm_provider": self.llm.active_provider,
        }

    def _handle_report(
        self,
        text: str,
        history: Optional[List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        """
        Branch B — GLOBAL_REPORT.
        Fetches real-time analytics metrics and asks the LLM to produce a
        concise, human-friendly executive summary for travel agency management.
        """
        kpis = self.analytics.get_kpis()
        top_entries = self.analytics.get_vulnerabilities_table(limit=5).to_dict(orient="records")

        # Convert table rows into FAISS-compatible match dicts for the LLM prompt
        top_matches = [
            {
                "id": row.get("record_id", "CVE-XXXX"),
                "similarity_score": 0.95,
                "severity": row.get("severity", "CRITICAL"),
                "description": str(row.get("description", ""))[:300],
            }
            for row in top_entries
        ]

        report_query = (
            f"Génère un rapport synthétique d'intelligence cyber pour les dernières 24h "
            f"à destination des directeurs d'agences de voyage. "
            f"Données en temps réel : {kpis['total_threats']} menaces répertoriées, "
            f"{kpis['critical_count']} critiques, score de risque global {kpis['global_risk_score']}/100. "
            f"État : {kpis['cyber_health']}."
        )

        response_text = self.llm.generate_advisory(
            query=report_query,
            intent=Intent.GLOBAL_REPORT.value,
            retrieved_matches=top_matches,
            history=history,
            system_metrics=kpis,
        )

        return {
            "query": text,
            "intent": Intent.GLOBAL_REPORT.value,
            "response_text": response_text,
            "modules_used": {"faiss": False, "distilbert": False, "llm": True, "analytics": True},
            "matches": top_matches,
            "severity": "CRITICAL" if kpis["global_risk_score"] > 70 else "HIGH",
            "confidence": 0.92,
            "llm_provider": self.llm.active_provider,
        }

    def _handle_cyber_threat(
        self,
        text: str,
        history: Optional[List[Dict[str, str]]],
        top_k: int,
    ) -> Dict[str, Any]:
        """
        Branch C — CYBER_THREAT.
        Full RAG pipeline: FAISS semantic search → optional DistilBERT severity
        classification → LLM targeted security advisory.
        """
        # Step 1 — FAISS semantic search
        matches: List[Dict[str, Any]] = []
        try:
            matches = self.vector_store.search(text, k=top_k)
            LOGGER.info("FAISS returned %d matches for query '%.60s'", len(matches), text)
        except Exception as err:
            LOGGER.error("FAISS search failed for '%.60s': %s", text, err, exc_info=True)
            # Continue without FAISS context — LLM will still answer from its knowledge
            LOGGER.warning("Proceeding without FAISS context due to search error.")

        # Step 2 — DistilBERT severity classification (optional, degrades gracefully)
        severity: Optional[str] = None
        confidence: Optional[float] = None

        if self.predictor is not None:
            try:
                pred = self.predictor.predict(text)
                severity = str(pred["severity"])
                confidence = float(pred["confidence"])
                LOGGER.debug("DistilBERT: severity=%s confidence=%.2f", severity, confidence)
            except Exception as err:
                LOGGER.error("DistilBERT prediction failed: %s", err, exc_info=True)
                # Do not fall back to hardcoded values — keep None to signal unavailability
        else:
            LOGGER.debug("DistilBERT predictor not loaded — severity scoring skipped.")

        # Step 3 — LLM advisory generation
        response_text = self.llm.generate_advisory(
            query=text,
            intent=Intent.CYBER_THREAT.value,
            severity=severity,
            confidence=confidence,
            retrieved_matches=matches,
            history=history,
        )

        return {
            "query": text,
            "intent": Intent.CYBER_THREAT.value,
            "response_text": response_text,
            "modules_used": {
                "faiss": True,
                "distilbert": self.predictor is not None,
                "llm": True,
                "analytics": False,
            },
            "matches": matches,
            "severity": severity,
            "confidence": confidence,
            "llm_provider": self.llm.active_provider,
        }

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _error_response(
        query: str,
        intent: Intent,
        message: str,
    ) -> Dict[str, Any]:
        """Build a standardised error response payload."""
        return {
            "query": query,
            "intent": intent.value,
            "response_text": f"⚠️ {message}",
            "modules_used": {"faiss": False, "distilbert": False, "llm": False, "analytics": False},
            "matches": [],
            "severity": None,
            "confidence": None,
            "llm_provider": "none",
        }
