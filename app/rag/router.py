"""Intent router for intelligent conditional RAG pipeline execution."""

from __future__ import annotations

import logging
import re
from typing import Dict, List

LOGGER = logging.getLogger(__name__)

# Intent Constants
INTENT_THREAT_ANALYSIS = "THREAT_ANALYSIS"
INTENT_BUSINESS_ADVICE = "BUSINESS_ADVICE"
INTENT_GENERAL = "GENERAL"


class IntentRouter:
    """Classifies user queries into RAG routing categories."""

    def __init__(self) -> None:
        """Initialize keyword pattern lists for fast deterministic routing."""
        self.threat_keywords = [
            r"\battaque\b", r"\bvulnérabilité\b", r"\bvulnerab\b", r"\bransomware\b",
            r"\bmalware\b", r"\bvirus\b", r"\brce\b", r"\binjection\b", r"\bsqli\b",
            r"\bxss\b", r"\bbuffer overflow\b", r"\bexploit\b", r"\bpaye?ment\b",
            r"\bbreach\b", r"\bfuite\b", r"\bhack\b", r"\bintrusion\b", r"\bdenial of service\b",
            r"\bddos\b", r"\bcritical\b", r"\bexécuter du code\b", r"\bcode execution\b",
            r"\bdétecté\b", r"\baffecte notre\b"
        ]

        self.business_keywords = [
            r"\bagence[s]? de voyage\b", r"\btourisme\b", r"\bvoyageur[s]?\b",
            r"\bréservation[s]?\b", r"\bbilletterie\b", r"\brisque[s]? cyber\b",
            r"\brisque[s]? concernent\b", r"\bproteger les données\b", r"\bsecteur\b",
            r"\bconseil[s]?\b", r"\bbonnes pratiques\b", r"\bplateforme[s]? de réservation\b"
        ]

        self.general_keywords = [
            r"\bqu['’]est[- ]ce qu\b", r"\bc['’]est quoi\b", r"\bdéfinir\b",
            r"\bdéfinition\b", r"\bexpliquer\b", r"\bcomment fonctionne\b"
        ]

    def detect_intent(self, query: str, history: List[Dict[str, str]] | None = None) -> Dict[str, bool | str]:
        """Detect query intent and determine module execution flags.

        Args:
            query: User prompt text.
            history: Optional conversation history.

        Returns:
            Dictionary with intent_type and boolean flags for distilbert, faiss, llm.
        """
        text = query.lower().strip()

        # Check for explicit threat patterns
        is_threat = any(re.search(pat, text) for pat in self.threat_keywords)
        is_business = any(re.search(pat, text) for pat in self.business_keywords)
        is_general = any(re.search(pat, text) for pat in self.general_keywords)

        # Contextual history check: if previous message mentioned booking/API/threat and user asks "quais risques"
        if not is_threat and history:
            last_user_msg = " ".join([m.get("content", "").lower() for m in history if m.get("role") == "user"])
            if any(term in last_user_msg for term in ["api", "réservation", "système", "payement", "vulnerab"]):
                is_business = True

        if is_threat:
            intent = INTENT_THREAT_ANALYSIS
            use_distilbert = True
            use_faiss = True
        elif is_business:
            intent = INTENT_BUSINESS_ADVICE
            use_distilbert = False
            use_faiss = True
        elif is_general and not (is_threat or is_business):
            intent = INTENT_GENERAL
            use_distilbert = False
            use_faiss = False
        else:
            # Default fallback for ambiguous queries: business advice RAG
            intent = INTENT_BUSINESS_ADVICE
            use_distilbert = False
            use_faiss = True

        LOGGER.info("Detected intent '%s' (DistilBERT=%s, FAISS=%s, LLM=True)", intent, use_distilbert, use_faiss)

        return {
            "intent": intent,
            "use_distilbert": use_distilbert,
            "use_faiss": use_faiss,
            "use_llm": True,
        }
