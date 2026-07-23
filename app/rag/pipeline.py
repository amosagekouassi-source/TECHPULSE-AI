"""
TECHPULSE-AI — RAG Pipeline (Clean Architecture & 4-Case Decision Matrix)
===========================================================================
Conditional RAG pipeline implementing the 4-case decision matrix:

    CAS 1: GENERAL_CONVERSATION → Direct friendly LLM response (no FAISS, no CVEs)
    CAS 2: PREVENTIVE_SECURITY  → Architecture & GDS hardening guide (no emergency tone)
    CAS 3: CYBER_INCIDENT       → FAISS search + DistilBERT + Emergency remediation
    CAS 4: GLOBAL_REPORT        → Real-time analytics KPIs + Executive summary

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


class RAGPipeline:
    """
    Conditional RAG pipeline enforcing the 4-case decision matrix.
    """

    def __init__(
        self,
        model_reference: Optional[Path | str] = None,
        vector_store_dir: Path | str = Path("models/vector_store"),
        llm_provider: str = "auto",
    ) -> None:
        self.router = IntentRouter()
        self.llm = LLMGenerator(provider=llm_provider)
        self.analytics = CyberAnalyticsEngine()

        self.vector_store = FAISSVectorStore(index_dir=vector_store_dir)
        self.predictor: Optional[SeverityPredictor] = None

        model_path = Path(model_reference or "models/distilbert-severity")
        if model_path.is_dir():
            try:
                self.predictor = SeverityPredictor(model_reference=model_path)
                LOGGER.info("DistilBERT predictor loaded from %s", model_path)
            except Exception as err:
                LOGGER.warning("DistilBERT model unavailable: %s", err)

        self.reports = ReportGenerator(
            analytics_engine=self.analytics,
            llm_generator=self.llm,
        )

    def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        text = message.strip()
        if not text:
            return self._error_response(
                query="",
                intent=Intent.GENERAL_CONVERSATION,
                message="Le message ne peut pas être vide.",
            )

        intent = self.router.classify(text, history=history)
        LOGGER.info("Intent classified as '%s' for input: %.80s", intent.value, text)

        try:
            if intent == Intent.GENERAL_CONVERSATION:
                return self._handle_general(text, history)
            elif intent == Intent.PREVENTIVE_SECURITY:
                return self._handle_preventive(text, history)
            elif intent == Intent.CYBER_INCIDENT:
                return self._handle_incident(text, history, top_k)
            else:  # Intent.GLOBAL_REPORT
                return self._handle_report(text, history)
        except Exception as err:
            LOGGER.error("Pipeline error [intent=%s]: %s", intent.value, err, exc_info=True)
            return self._error_response(
                query=text,
                intent=intent,
                message="Une erreur inattendue s'est produite dans le pipeline RAG.",
            )

    def process_chat_message(self, query=None, message=None, history=None, top_k=5):
        return self.chat(message=query or message or "", history=history, top_k=top_k)

    def process_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        res = self.chat(message=query, history=None, top_k=top_k)
        res["advisory"] = res["response_text"]
        return res

    # ── CAS 1 : Salutations / Conversation Générale / État Système ─────────────
    def _handle_general(
        self,
        text: str,
        history: Optional[List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        system_metrics = None
        try:
            system_metrics = self.analytics.get_kpis()
        except Exception:
            pass

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
            "cves": [],
            "severity": None,
            "confidence": None,
            "llm_provider": self.llm.active_provider,
        }

    # ── CAS 2 : Sécurisation Préventive & Architecture GDS ────────────────────
    def _handle_preventive(
        self,
        text: str,
        history: Optional[List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        response_text = self.llm.generate_advisory(
            query=text,
            intent=Intent.PREVENTIVE_SECURITY.value,
            history=history,
        )

        return {
            "query": text,
            "intent": Intent.PREVENTIVE_SECURITY.value,
            "response_text": response_text,
            "modules_used": {"faiss": False, "distilbert": False, "llm": True, "analytics": False},
            "matches": [],
            "cves": [],
            "severity": None,
            "confidence": None,
            "llm_provider": self.llm.active_provider,
        }

    # ── CAS 3 : Incident / Attaque Active / Faille Spécifique ────────────────
    def _handle_incident(
        self,
        text: str,
        history: Optional[List[Dict[str, str]]],
        top_k: int,
    ) -> Dict[str, Any]:
        matches = []
        try:
            matches = self.vector_store.search(text, k=top_k)
        except Exception as err:
            LOGGER.warning("FAISS search unvailable: %s", err)

        severity = None
        confidence = None
        if self.predictor is not None:
            try:
                pred = self.predictor.predict(text)
                severity = str(pred["severity"])
                confidence = float(pred["confidence"])
            except Exception:
                pass

        response_text = self.llm.generate_advisory(
            query=text,
            intent=Intent.CYBER_INCIDENT.value,
            severity=severity,
            confidence=confidence,
            retrieved_matches=matches,
            history=history,
        )

        valid_cves = self.llm.extract_valid_cves(matches)

        return {
            "query": text,
            "intent": Intent.CYBER_INCIDENT.value,
            "response_text": response_text,
            "modules_used": {
                "faiss": True,
                "distilbert": self.predictor is not None,
                "llm": True,
                "analytics": False,
            },
            "matches": matches,
            "cves": valid_cves,
            "severity": severity or "HIGH",
            "confidence": confidence,
            "llm_provider": self.llm.active_provider,
        }

    # ── CAS 4 : Rapport Global / Bilan 24h ──────────────────────────────────
    def _handle_report(
        self,
        text: str,
        history: Optional[List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        kpis = self.analytics.get_kpis()

        response_text = self.llm.generate_advisory(
            query=text,
            intent=Intent.GLOBAL_REPORT.value,
            history=history,
            system_metrics=kpis,
        )

        return {
            "query": text,
            "intent": Intent.GLOBAL_REPORT.value,
            "response_text": response_text,
            "modules_used": {"faiss": False, "distilbert": False, "llm": True, "analytics": True},
            "matches": [],
            "cves": [],
            "severity": "HIGH",
            "confidence": 0.95,
            "llm_provider": self.llm.active_provider,
        }

    @staticmethod
    def _error_response(query: str, intent: Intent, message: str) -> Dict[str, Any]:
        return {
            "query": query,
            "intent": intent.value,
            "response_text": f"⚠️ {message}",
            "modules_used": {"faiss": False, "distilbert": False, "llm": False, "analytics": False},
            "matches": [],
            "cves": [],
            "severity": None,
            "confidence": None,
            "llm_provider": "none",
        }
