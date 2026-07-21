"""Report generator module for executive threat reports in TECHPULSE-AI."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.analytics.engine import CyberAnalyticsEngine
from app.llm.client import LLMGenerator

LOGGER = logging.getLogger(__name__)


class ReportGenerator:
    """Generates synthetic executive cybersecurity threat reports for travel platforms."""

    def __init__(
        self,
        analytics_engine: Optional[CyberAnalyticsEngine] = None,
        llm_generator: Optional[LLMGenerator] = None,
    ) -> None:
        """Initialize ReportGenerator.

        Args:
            analytics_engine: Instance of CyberAnalyticsEngine.
            llm_generator: Instance of LLMGenerator.
        """
        self.analytics = analytics_engine or CyberAnalyticsEngine()
        self.llm = llm_generator or LLMGenerator()

    def generate_recent_threats_report(self, query: str = "Rapport 24h menaces récentes") -> str:
        """Generate structured executive cybersecurity report for the last 24h/recent window."""
        kpis = self.analytics.get_kpis()
        top_cves = self.analytics.get_vulnerabilities_table(limit=5).to_dict(orient="records")

        matches = [
            {
                "id": row.get("record_id", "CVE"),
                "similarity_score": 0.95,
                "severity": row.get("severity", "CRITICAL"),
                "description": row.get("description", "Description de vulnérabilité"),
            }
            for row in top_cves
        ]

        report = self.llm.generate_advisory(
            query=f"Générer le rapport synthétique d'intelligence cyber des dernières 24h pour agences de voyage. (Menaces totales: {kpis['total_threats']}, Critiques: {kpis['critical_count']}, Score Risque: {kpis['global_risk_score']}/100)",
            intent="REPORT_REQUEST",
            severity="CRITICAL" if kpis["global_risk_score"] > 70 else "HIGH",
            confidence=0.92,
            retrieved_matches=matches,
            history=None,
        )

        return report
