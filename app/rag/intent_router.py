"""
TECHPULSE-AI — Intent Router (4-Case Decision Matrix Architecture)
===================================================================
Classifies user queries into exactly 4 decision matrix categories:

    CAS 1: GENERAL_CONVERSATION → Greetings, system status, generic friendly interaction
    CAS 2: PREVENTIVE_SECURITY  → Architecture best practices (OAuth2, mTLS, Rate Limiting, PCI-DSS, CVE definitions)
    CAS 3: CYBER_INCIDENT       → Active attack detection, specific CVE flaw analysis, ransomware, RCE, emergency remediation
    CAS 4: GLOBAL_REPORT        → 24h activity summaries, executive threat reports

Author: TECHPULSE-AI Engineering
"""

from __future__ import annotations

import logging
import re
from enum import Enum
from typing import List, Optional, Tuple

LOGGER = logging.getLogger(__name__)


class Intent(str, Enum):
    """The 4 decision matrix routing destinations."""
    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    PREVENTIVE_SECURITY  = "PREVENTIVE_SECURITY"
    CYBER_INCIDENT       = "CYBER_INCIDENT"
    GLOBAL_REPORT        = "GLOBAL_REPORT"


_REPORT_PATTERNS: List[str] = [
    r"\bdernière[s]?\s*24\s*h\b",
    r"\bces\s+dernières\s+24\s*h\b",
    r"\bderniere[s]?\s*24\s*h\b",
    r"\brapport\s+(de\s+sécurité|de\s+securite|24h|mensuel|hebdomadaire|d['']activité)\b",
    r"\bgénère[r]?\s+un\s+rapport\b",
    r"\bgenere[r]?\s+un\s+rapport\b",
    r"\bsynthèse\s+des\s+menaces\b",
    r"\bbilan\s+(global|des\s+menaces|de\s+sécurité)\b",
    r"\bque\s+s['']est[- ]il\s+passé\b",
    r"\brapport\s+exécutif\b",
    r"\bactivité\s+(récente|des\s+dernières)\b",
]

_INCIDENT_PATTERNS: List[str] = [
    # Explicit CVE identifiers (e.g. CVE-2025-1429)
    r"\bcve-\d{4}-\d+\b",
    # Active attack & malware terms
    r"\b(ransomware|malware|spyware|trojan|phishing)\b",
    r"\b(rce|lfi|rfi|ssrf|sqli|xss|csrf|idor|xxe)\b",
    r"\b(injection|buffer\s+overflow|race\s+condition|privilege\s+escalation)\b",
    r"\b(zero[- ]day|0day|exploit|payload|backdoor|porte\s+dérobée)\b",
    r"\b(ddos|botnet|c2\s+server|command.and.control)\b",
    r"\b(data\s+breach|fuite\s+de\s+données|exfiltration|leak)\b",
    r"\b(subissons|attaque\s+en\s+cours|incident\s+critique|intrusion|compromis[s]?)\b",
    r"\b(faille\s+critique|vulnérabilité\s+critique|attaque)\b",
]

_PREVENTIVE_PATTERNS: List[str] = [
    # GDS & Travel API hardening
    r"\b(sécuriser|securiser|protéger|proteger|hardening|chiffrement|cryptage)\b",
    r"\b(api\s+(amadeus|sabre|travelport|gds)|système\s+de\s+réservation)\b",
    r"\b(pci[- ]dss|conformité\s+pci|passerelle\s+de\s+paiement)\b",
    r"\b(bonnes?\s+pratiques?|recommandations?\s+de\s+sécurité|architecture\s+sécurisée)\b",
    r"\b(oauth|mtls|rate\s+limiting|jwt|token|certificat\s+ssl|tls|https)\b",
    # Definitions (e.g. Qu'est-ce qu'une CVE)
    r"\bqu['']est[- ]ce\s+qu['']une?\s+cve\b",
    r"\bc['']est\s+quoi\s+une?\s+cve\b",
    r"\bdéfinition\s+(de\s+la\s+)?cve\b",
]

_GENERAL_PATTERNS: List[str] = [
    r"^\s*(bonjour|salut|hello|bonsoir|hey|coucou|hi)\b",
    r"\bcomment\s+vas[- ]tu\b",
    r"\b(qui\s+es[- ]tu|pr[eé]sente[- ]toi|que\s+fais[- ]tu)\b",
    r"\b(c['']est\s+quoi\s+techpulse|techpulse[- ]ai)\b",
    r"\b(etat|[eé]tat)\s+(du\s+syst[eè]me|actuel)\b",
    r"\b(statut|status)\s+(du\s+syst[eè]me|des\s+services)\b",
    r"\bbilan\s+syst[eè]me\b",
    r"\btout\s+fonctionne\b",
    r"\b(merci|parfait|super|d['']accord)\b",
]


def _compile(patterns: List[str]) -> List[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


class IntentRouter:
    """
    4-Case Decision Matrix Classifier.
    """

    def __init__(self) -> None:
        self._report_re     = _compile(_REPORT_PATTERNS)
        self._incident_re   = _compile(_INCIDENT_PATTERNS)
        self._preventive_re = _compile(_PREVENTIVE_PATTERNS)
        self._general_re    = _compile(_GENERAL_PATTERNS)

    @staticmethod
    def _match_any(patterns: List[re.Pattern[str]], text: str) -> bool:
        return any(p.search(text) for p in patterns)

    def classify(
        self,
        query: str,
        history: Optional[List[dict]] = None,
    ) -> Intent:
        text = query.strip()

        # ── 1. CAS 4 : Rapport global / Bilan 24h ─────────────
        if self._match_any(self._report_re, text):
            LOGGER.debug("[IntentRouter] CAS 4 (GLOBAL_REPORT) ← '%s'", text[:80])
            return Intent.GLOBAL_REPORT

        # ── 2. CAS 3 : Incident en cours / Attaque / CVE spécifique ──────────
        if self._match_any(self._incident_re, text):
            LOGGER.debug("[IntentRouter] CAS 3 (CYBER_INCIDENT) ← '%s'", text[:80])
            return Intent.CYBER_INCIDENT

        # ── 3. CAS 2 : Sécurisation préventive & Architecture ──────────────────
        if self._match_any(self._preventive_re, text):
            LOGGER.debug("[IntentRouter] CAS 2 (PREVENTIVE_SECURITY) ← '%s'", text[:80])
            return Intent.PREVENTIVE_SECURITY

        # ── 4. CAS 1 : Salutations / Bilan système / Discussion générale ─────
        if self._match_any(self._general_re, text):
            LOGGER.debug("[IntentRouter] CAS 1 (GENERAL_CONVERSATION) ← '%s'", text[:80])
            return Intent.GENERAL_CONVERSATION

        # ── 5. Fallback ───────────────────────────────────────────────────────
        q_lower = text.lower()
        if any(kw in q_lower for kw in ("comment", "securis", "sécuris", "api", "gds", "amadeus", "sabre", "pci")):
            return Intent.PREVENTIVE_SECURITY

        return Intent.GENERAL_CONVERSATION

    def detect_intent(self, query: str, history: Optional[List[dict]] = None) -> dict:
        """Legacy compatibility wrapper."""
        intent = self.classify(query, history)
        return {
            "intent": intent.value,
            "use_distilbert": intent == Intent.CYBER_INCIDENT,
            "use_faiss": intent == Intent.CYBER_INCIDENT,
            "use_llm": True,
            "use_reports": intent == Intent.GLOBAL_REPORT,
        }


# Backwards compatibility constants
INTENT_GENERAL_QUESTION = Intent.GENERAL_CONVERSATION.value
INTENT_CYBER_QUESTION   = Intent.PREVENTIVE_SECURITY.value
INTENT_THREAT_ANALYSIS  = Intent.CYBER_INCIDENT.value
INTENT_CVE_ANALYSIS     = Intent.CYBER_INCIDENT.value
INTENT_REPORT_REQUEST   = Intent.GLOBAL_REPORT.value
