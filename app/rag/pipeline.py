"""RAG Pipeline connecting Intent Router, FAISS Vector Store, DistilBERT Classifier, Report Generator, and LLM."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.classifier.predict import SeverityPredictor
from app.vector_store.faiss_store import FAISSVectorStore
from app.llm.client import LLMGenerator
from app.rag.router import (
    IntentRouter,
    INTENT_GENERAL_QUESTION,
    INTENT_CYBER_QUESTION,
    INTENT_THREAT_ANALYSIS,
    INTENT_CVE_ANALYSIS,
    INTENT_REPORT_REQUEST,
)
from app.reports.generator import ReportGenerator
from app.analytics.engine import CyberAnalyticsEngine

LOGGER = logging.getLogger(__name__)


class RAGPipeline:
    """Conditional RAG pipeline integrating 5-Intent Router -> DistilBERT -> FAISS -> LLM -> Reports."""

    def __init__(
        self,
        model_reference: Optional[Path | str] = None,
        vector_store_dir: Path | str = Path("models/vector_store"),
        llm_provider: str = "auto",
    ) -> None:
        """Initialize RAG pipeline components."""
        self.router = IntentRouter()
        self.vector_store = FAISSVectorStore(index_dir=vector_store_dir)
        self.llm = LLMGenerator(provider=llm_provider)
        self.analytics = CyberAnalyticsEngine()
        self.reports = ReportGenerator(analytics_engine=self.analytics, llm_generator=self.llm)
        self.predictor: Optional[SeverityPredictor] = None

        model_path = Path(model_reference or "models/distilbert-severity")
        if model_path.is_dir():
            try:
                self.predictor = SeverityPredictor(model_reference=model_path)
                LOGGER.info("Loaded DistilBERT predictor from %s", model_path)
            except Exception as err:
                LOGGER.warning("Could not load DistilBERT model: %s", err)

    def process_chat_message(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Process a chat prompt through conditional RAG routing across 5 intent categories.

        Args:
            query: Input user text prompt.
            history: Conversation history list.
            top_k: Top k vector search matches.

        Returns:
            Dictionary containing response_text, intent, modules_used, matches, severity, and confidence.
        """
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty")

        # 1. Intent Routing
        routing = self.router.detect_intent(query, history=history)
        intent = str(routing["intent"])
        use_distilbert = bool(routing["use_distilbert"])
        use_faiss = bool(routing["use_faiss"])
        use_llm = bool(routing["use_llm"])
        use_reports = bool(routing["use_reports"])

        # Special Case: REPORT_REQUEST intent
        if intent == INTENT_REPORT_REQUEST:
            report_text = self.reports.generate_recent_threats_report(query=query)
            return {
                "query": query,
                "intent": intent,
                "modules_used": {
                    "distilbert": False,
                    "faiss": True,
                    "llm": True,
                    "collector": True,
                    "analytics": True,
                },
                "severity": "HIGH",
                "confidence": 0.90,
                "matches": [],
                "response_text": report_text,
                "llm_provider": self.llm.active_provider,
            }

        # 2. Conditional DistilBERT Severity Classification
        severity: Optional[str] = None
        confidence: Optional[float] = None
        if use_distilbert:
            if self.predictor is not None:
                try:
                    pred = self.predictor.predict(query)
                    severity = str(pred["severity"])
                    confidence = float(pred["confidence"])
                except Exception as err:
                    LOGGER.error("DistilBERT prediction error: %s", err)
                    severity, confidence = "HIGH", 0.85
            else:
                query_upper = query.upper()
                if "CRITICAL" in query_upper or "EXECUTION" in query_upper or "RCE" in query_upper:
                    severity, confidence = "CRITICAL", 0.90
                else:
                    severity, confidence = "HIGH", 0.82

        # 3. Conditional FAISS Vector Search Retrieval
        matches: List[Dict[str, Any]] = []
        if use_faiss:
            try:
                matches = self.vector_store.search(query, k=top_k)
            except Exception as err:
                LOGGER.error("FAISS vector search error: %s", err)

        # 4. LLM Generation
        response_text = self.llm.generate_advisory(
            query=query,
            intent=intent,
            severity=severity,
            confidence=confidence,
            retrieved_matches=matches,
            history=history,
        )

        return {
            "query": query,
            "intent": intent,
            "modules_used": {
                "distilbert": use_distilbert,
                "faiss": use_faiss,
                "llm": use_llm,
                "collector": True,
                "analytics": True,
            },
            "severity": severity,
            "confidence": confidence,
            "matches": matches,
            "response_text": response_text,
            "llm_provider": self.llm.active_provider,
        }

    def process_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Backwards compatibility wrapper for single query execution."""
        res = self.process_chat_message(query, history=None, top_k=top_k)
        res["advisory"] = res["response_text"]
        return res
