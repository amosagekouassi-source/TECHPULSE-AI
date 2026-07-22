"""
TECHPULSE-AI — Intent Router (3-Intent Architecture)
=====================================================
Classifies user queries into exactly 3 routing categories:

    GENERAL_CONVERSATION   →  Greetings, definitions, system status, generic tech questions
    GLOBAL_REPORT          →  24h activity summaries or executive threat reports
    CYBER_THREAT           →  Specific CVE/vulnerability/attack queries, travel asset security

The router uses ordered regex pattern matching with an explicit priority chain:
    1. Report patterns   (highest specificity)
    2. Cyber/threat patterns
    3. General patterns  (catch-all last)

Author: TECHPULSE-AI Engineering
"""

from __future__ import annotations

import logging
import re
from enum import Enum
from typing import List, Optional, Tuple

LOGGER = logging.getLogger(__name__)


class Intent(str, Enum):
    """The 3 possible routing destinations for a user query."""
    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    GLOBAL_REPORT        = "GLOBAL_REPORT"
    CYBER_THREAT         = "CYBER_THREAT"


# ---------------------------------------------------------------------------
# Pattern Catalogue
# Each entry is a raw regex string, matched case-insensitively against the
# lowercased, stripped user input.
# ---------------------------------------------------------------------------

_REPORT_PATTERNS: List[str] = [
    # With accents
    r"\bdernière[s]?\s*24\s*h\b",
    r"\bces\s+dernières\s+24\s*h\b",
    r"\brapport\s+(de\s+sécurité|24h|mensuel|hebdomadaire|d['']activité)\b",
    r"\bgénère[r]?\s+un\s+rapport\b",
    r"\bgénér[eé][r]?\s+(un\s+)?rapport\b",
    r"\bsynthèse\s+des\s+menaces\b",
    r"\bbilan\s+(global|des\s+menaces|de\s+sécurité)\b",
    r"\bque\s+s['']est[- ]il\s+passé\b",
    r"\bquoi\s+de\s+neuf\s+(en\s+cyber|côté\s+sécurité)\b",
    r"\brapport\s+exécutif\b",
    r"\bactivité\s+(récente|des\s+dernières)\b",
    # Without accents (user may type without French diacritics)
    r"\bderniere[s]?\s*24\s*h\b",
    r"\bces\s+dernieres\s*24\s*h\b",
    r"\brapport\s+(de\s+securite|d['']activite)\b",
    r"\bgenere[r]?\s+un\s+rapport\b",
    r"\bsynthese\s+des\s+menaces\b",
    r"\bbilan\s+(des\s+menaces|de\s+securite)\b",
    r"\bque\s+s['']est[- ]il\s+passe\b",
    r"\brapport\s+executif\b",
    r"\bactivite\s+recente\b",
    # Short trigger variants
    r"\brapport\s+24h\b",
    r"\brapport\s+mensuel\b",
    r"\brapport\s+hebdomadaire\b",
]

_CYBER_PATTERNS: List[str] = [
    # CVE identifiers
    r"\bcve-\d{4}-\d+\b",
    # Attack types
    r"\b(ransomware|malware|spyware|trojan|phishing)\b",
    r"\b(rce|lfi|rfi|ssrf|sqli|xss|csrf|idor|xxe)\b",
    r"\b(injection|buffer\s+overflow|race\s+condition|privilege\s+escalation)\b",
    r"\b(zero[- ]day|0day|exploit|payload|backdoor|porte\s+dérobée)\b",
    r"\b(ddos|denial.of.service|botnet|c2\s+server|command.and.control)\b",
    r"\b(data\s+breach|fuite\s+de\s+données|exfiltration|leak)\b",
    # Security actions
    r"\b(patch|correctif|mise\s+à\s+jour\s+de\s+sécurité|remédiation|mitigation)\b",
    r"\b(firewall|waf|ids|ips|siem|soc|pentest|audit\s+de\s+sécurité)\b",
    r"\b(authentification|oauth|jwt|token|clé\s+api|api\s+key)\b",
    # Vulnerability terms
    r"\b(vulnérabilité[s]?|vulnerability|faille[s]?|weakness)\b",
    r"\b(attaque[s]?|intrusion|compromis[s]?|incident)\b",
    r"\b(risque[s]?\s+(cyber|de\s+sécurité)|menace[s]?\s+cyber)\b",
    # Travel sector targets
    r"\b(api\s+(amadeus|sabre|travelport|gds)|système\s+de\s+réservation)\b",
    r"\b(pci[- ]dss|conformité\s+pci|passerelle\s+de\s+paiement)\b",
    r"\b(données\s+(voyageurs|personnelles|bancaires|passeport))\b",
    r"\b(sécuriser|protéger|hardening|chiffrement|cryptage)\b",
    r"\b(certificat\s+ssl|tls|https|hsts|cors)\b",
]

_GENERAL_PATTERNS: List[str] = [
    # Greetings
    r"^\s*(bonjour|salut|hello|bonsoir|hey|coucou|hi)\b",
    # Self-introduction / identity
    r"\b(qui\s+es[- ]tu|presente[- ]toi|que\s+fais[- ]tu|decris[- ]toi)\b",
    r"\b(qui\s+es[- ]tu|pr[eé]sente[- ]toi|que\s+fais[- ]tu|d[eé]cris[- ]toi)\b",
    r"\b(c['']est\s+quoi\s+techpulse|techpulse[- ]ai\s+c['']est)\b",
    # System status — with and without accents
    r"\b(etat|[eé]tat)\s+(du\s+syst[eè]me|actuel)\b",
    r"\b(statut|status)\s+(du\s+syst[eè]me|des\s+composants)\b",
    r"\b(bilan\s+sur\s+l['']([eé]tat)|[eé]tat\s+actuel\s+du\s+syst[eè]me)\b",
    r"\btout\s+fonctionne\b",
    r"\bsyst[eè]me\s+ok\b",
    r"\b(es[- ]tu|[eê]tes[- ]vous)\s+(op[eé]rationnel|disponible)\b",
    r"\bcomment\s+vas[- ]tu\b",
    # General knowledge / definitions
    r"\bqu['']est[- ]ce\s+qu['']\b",
    r"\bc['']est\s+quoi\s+(une?|le|la|les)\s+\b",
    r"\b(d[eé]finition\s+de|expliqu[eez])\b",
    r"\bcomment\s+fonctionne\b",
    r"\bc['']est\s+quoi\s+le\s+principe\b",
    # Generic help / conversational
    r"\b(aide[- ]moi|help|tu\s+peux\s+m['']aider|que\s+peux[- ]tu\s+faire)\b",
    r"\b(merci|parfait|super|d['']accord|bien\s+re[cç]u)\b",
]


def _compile(patterns: List[str]) -> List[re.Pattern[str]]:
    """Compile regex patterns to case-insensitive objects."""
    return [re.compile(p, re.IGNORECASE) for p in patterns]


class IntentRouter:
    """
    Deterministic 3-intent classifier using regex pattern matching.

    Priority order (first match wins):
        1. GLOBAL_REPORT  — high specificity, explicit report/summary requests
        2. CYBER_THREAT   — attack/CVE/vulnerability/travel-asset security
        3. GENERAL_CONVERSATION — greetings, definitions, system status
        4. Fallback heuristic — query length as tiebreaker (long = CYBER_THREAT)
    """

    def __init__(self) -> None:
        self._report_re  = _compile(_REPORT_PATTERNS)
        self._cyber_re   = _compile(_CYBER_PATTERNS)
        self._general_re = _compile(_GENERAL_PATTERNS)

    @staticmethod
    def _match_any(patterns: List[re.Pattern[str]], text: str) -> bool:
        """Return True if any pattern in the list matches the given text."""
        return any(p.search(text) for p in patterns)

    def classify(
        self,
        query: str,
        history: Optional[List[dict]] = None,
    ) -> Intent:
        """
        Classify a user query into one of the 3 intents.

        Args:
            query:   Raw user input string (will be stripped internally).
            history: Optional conversation history (used for context enrichment).

        Returns:
            Intent enum value.
        """
        text = query.strip()

        # ── 1. Report request — checked first (highest specificity) ──────────
        if self._match_any(self._report_re, text):
            LOGGER.debug("[IntentRouter] GLOBAL_REPORT ← '%s'", text[:80])
            return Intent.GLOBAL_REPORT

        # ── 2. Cyber / threat / CVE query ────────────────────────────────────
        if self._match_any(self._cyber_re, text):
            LOGGER.debug("[IntentRouter] CYBER_THREAT ← '%s'", text[:80])
            return Intent.CYBER_THREAT

        # ── 3. General conversation / definition / system status ─────────────
        if self._match_any(self._general_re, text):
            LOGGER.debug("[IntentRouter] GENERAL_CONVERSATION (pattern) ← '%s'", text[:80])
            return Intent.GENERAL_CONVERSATION

        # ── 4. Context-aware fallback — check conversation history ───────────
        if history:
            past_text = " ".join(
                m.get("content", "") for m in history if m.get("role") == "user"
            ).lower()
            if any(kw in past_text for kw in ("cve", "api", "attaque", "exploit", "réservation")):
                LOGGER.debug("[IntentRouter] CYBER_THREAT (history fallback) ← '%s'", text[:80])
                return Intent.CYBER_THREAT

        # ── 5. Length heuristic — long queries are likely technical ──────────
        intent = Intent.CYBER_THREAT if len(text) > 40 else Intent.GENERAL_CONVERSATION
        LOGGER.debug("[IntentRouter] %s (heuristic len=%d) ← '%s'", intent.value, len(text), text[:80])
        return intent

    # -----------------------------------------------------------------------
    # Legacy compatibility — existing code that calls detect_intent()
    # -----------------------------------------------------------------------

    def detect_intent(
        self,
        query: str,
        history: Optional[List[dict]] = None,
    ) -> dict:
        """
        Legacy compatibility shim.
        Maps the new 3-intent model back to the old dict-based response format
        so existing callers (Streamlit dashboard, tests, etc.) don't break.
        """
        intent = self.classify(query, history)

        # Map to old flag schema
        use_faiss     = intent == Intent.CYBER_THREAT
        use_distilbert = intent == Intent.CYBER_THREAT
        use_reports   = intent == Intent.GLOBAL_REPORT

        return {
            "intent":        intent.value,
            "use_distilbert": use_distilbert,
            "use_faiss":      use_faiss,
            "use_llm":        True,
            "use_reports":    use_reports,
        }


# ---------------------------------------------------------------------------
# Module-level helper (used by pipeline.py imports)
# ---------------------------------------------------------------------------

# Expose old string constants for backwards compat (e.g. Streamlit dashboard)
INTENT_GENERAL_QUESTION = Intent.GENERAL_CONVERSATION.value
INTENT_CYBER_QUESTION   = Intent.CYBER_THREAT.value
INTENT_THREAT_ANALYSIS  = Intent.CYBER_THREAT.value
INTENT_CVE_ANALYSIS     = Intent.CYBER_THREAT.value
INTENT_REPORT_REQUEST   = Intent.GLOBAL_REPORT.value
