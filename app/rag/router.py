"""Intent router for intelligent conditional RAG pipeline execution."""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional

LOGGER = logging.getLogger(__name__)

# Intent Constants
INTENT_GENERAL_QUESTION = "GENERAL_QUESTION"
INTENT_CYBER_QUESTION = "CYBER_QUESTION"
INTENT_THREAT_ANALYSIS = "THREAT_ANALYSIS"
INTENT_CVE_ANALYSIS = "CVE_ANALYSIS"
INTENT_REPORT_REQUEST = "REPORT_REQUEST"


class IntentRouter:
    """Classifies user queries into 5 RAG routing categories."""

    def __init__(self) -> None:
        """Initialize pattern matchers for deterministic intent classification."""
        self.greetings_patterns = [
            r"^\s*bonjour\b", r"^\s*salut\b", r"^\s*hello\b", r"^\s*coucou\b", r"^\s*hi\b"
        ]

        self.report_patterns = [
            r"\brapport\b", r"\bdernière[s]? 24h\b", r"\b24h\b", r"\bce mois-ci\b",
            r"\bmenaces récente[s]?\b", r"\bbilan\b", r"\bsynthèse des menaces\b"
        ]

        self.cve_patterns = [
            r"\bcve-\d{4}-\d+\b", r"\bexplique cve\b", r"\banalyse[r]? cve\b", r"\bdétail cve\b"
        ]

        self.threat_patterns = [
            r"\battaque\b", r"\bvulnérabilité\b", r"\bransomware\b", r"\bmalware\b",
            r"\brce\b", r"\binjection\b", r"\bsqli\b", r"\bxss\b", r"\bbuffer overflow\b",
            r"\bexploit\b", r"\bbreach\b", r"\bfuite\b", r"\bhack\b", r"\bintrusion\b",
            r"\bdenial of service\b", r"\bddos\b", r"\bexécuter du code\b", r"\bdétecté\b",
            r"\baffecte notre\b", r"\bcode execution\b", r"\bporte dérobée\b"
        ]

        self.cyber_patterns = [
            r"\brisque[s]?\b", r"\bagence[s]? de voyage\b", r"\btourisme\b", r"\bvoyageur[s]?\b",
            r"\bréservation[s]?\b", r"\bbilletterie\b", r"\bproteger\b", r"\bprotéger\b",
            r"\bsecuriser\b", r"\bsécuriser\b", r"\bfraude\b", r"\bbonnes pratiques\b",
            r"\bconseil[s]?\b", r"\bsecteur\b"
        ]

        self.general_def_patterns = [
            r"\bqu['’]est[- ]ce qu\b", r"\bc['’]est quoi\b", r"\bdéfinir\b", r"\bdéfinition\b",
            r"\bcomment fonctionne\b"
        ]

    def detect_intent(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Classify prompt text into one of 5 intent categories.

        Args:
            query: Input prompt string.
            history: Optional conversation history.

        Returns:
            Dictionary containing intent_type and boolean module execution flags.
        """
        text = query.lower().strip()

        # 1. Check for greetings or simple general questions
        is_greeting = any(re.search(pat, text) for pat in self.greetings_patterns)
        is_report = any(re.search(pat, text) for pat in self.report_patterns)
        is_cve = any(re.search(pat, text) for pat in self.cve_patterns)
        is_threat = any(re.search(pat, text) for pat in self.threat_patterns)
        is_cyber = any(re.search(pat, text) for pat in self.cyber_patterns)
        is_general_def = any(re.search(pat, text) for pat in self.general_def_patterns)

        # Contextual check: if follow-up refers to earlier system/API topic
        if not (is_threat or is_cve or is_report) and history:
            user_past = " ".join([m.get("content", "").lower() for m in history if m.get("role") == "user"])
            if any(term in user_past for term in ["api", "réservation", "billetterie", "cve", "attaque"]):
                is_cyber = True

        # Classify intent & set pipeline execution flags
        if is_report:
            intent = INTENT_REPORT_REQUEST
            use_distilbert = False
            use_faiss = True
            use_reports = True
        elif is_cve:
            intent = INTENT_CVE_ANALYSIS
            use_distilbert = True
            use_faiss = True
            use_reports = False
        elif is_threat:
            intent = INTENT_THREAT_ANALYSIS
            use_distilbert = True
            use_faiss = True
            use_reports = False
        elif is_cyber:
            intent = INTENT_CYBER_QUESTION
            use_distilbert = False
            use_faiss = True
            use_reports = False
        elif is_greeting or (is_general_def and not (is_threat or is_cve)):
            intent = INTENT_GENERAL_QUESTION
            use_distilbert = False
            use_faiss = False
            use_reports = False
        else:
            # Fallback for general questions vs business questions
            intent = INTENT_CYBER_QUESTION if len(text) > 25 else INTENT_GENERAL_QUESTION
            use_distilbert = False
            use_faiss = (intent == INTENT_CYBER_QUESTION)
            use_reports = False

        LOGGER.info(
            "Detected intent '%s' (DistilBERT=%s, FAISS=%s, LLM=True, Reports=%s)",
            intent, use_distilbert, use_faiss, use_reports
        )

        return {
            "intent": intent,
            "use_distilbert": use_distilbert,
            "use_faiss": use_faiss,
            "use_llm": True,
            "use_reports": use_reports,
        }
