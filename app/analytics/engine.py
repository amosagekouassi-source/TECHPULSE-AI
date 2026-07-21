"""Cyber Analytics Engine for TECHPULSE-AI Intelligence Dashboard."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

LOGGER = logging.getLogger(__name__)


class CyberAnalyticsEngine:
    """Analytics engine processing techpulse_dataset.parquet for executive metrics and charts."""

    def __init__(self, parquet_path: Path | str = Path("data/processed/techpulse_dataset.parquet")) -> None:
        """Initialize analytics engine and load dataset.

        Args:
            parquet_path: Path to dataset parquet file.
        """
        self.parquet_path = Path(parquet_path)
        self.df: pd.DataFrame = pd.DataFrame()
        self.load_dataset()

    def load_dataset(self) -> None:
        """Load and prepare parquet dataset."""
        if not self.parquet_path.is_file():
            LOGGER.warning("Parquet dataset not found at %s. Analytics will use synthetic fallback.", self.parquet_path)
            self._init_synthetic_fallback()
            return

        try:
            self.df = pd.read_parquet(self.parquet_path)
            LOGGER.info("Loaded %d rows for CyberAnalyticsEngine", len(self.df))
        except Exception as err:
            LOGGER.error("Error reading parquet dataset: %s", err)
            self._init_synthetic_fallback()

    def get_kpis(self) -> Dict[str, Any]:
        """Compute executive KPI metrics for Tab 1 Dashboard."""
        if self.df.empty:
            return {
                "total_threats": 0,
                "critical_count": 0,
                "cve_count": 0,
                "global_risk_score": 0,
                "cyber_health": "🟢 Inconnu",
            }

        total_threats = len(self.df)
        critical_count = len(self.df[self.df["severity"].str.upper() == "CRITICAL"])
        high_count = len(self.df[self.df["severity"].str.upper() == "HIGH"])
        
        cve_mask = self.df["source"].astype(str).str.upper().str.contains("CVE") | self.df["record_id"].astype(str).str.upper().str.startswith("CVE")
        cve_count = len(self.df[cve_mask])

        # Calculate Global Risk Score (0 - 100)
        risk_score = min(100, int((critical_count * 2.5 + high_count * 1.2) / max(1, total_threats) * 100 + 45))

        if risk_score >= 75:
            cyber_health = "🚨 Risque Critique - Action d'urgence requis"
        elif risk_score >= 50:
            cyber_health = "⚠️ Risque Élevé - Remédiation prioritaire"
        else:
            cyber_health = "🟢 Risque Modéré - Surveillance continue"

        return {
            "total_threats": total_threats,
            "critical_count": critical_count,
            "cve_count": cve_count,
            "global_risk_score": risk_score,
            "cyber_health": cyber_health,
        }

    def get_severity_distribution(self) -> pd.DataFrame:
        """Get severity breakdown for Streamlit bar chart."""
        if self.df.empty or "severity" not in self.df.columns:
            return pd.DataFrame({"Sévérité": ["CRITICAL", "HIGH", "MEDIUM", "LOW"], "Nombre": [15, 30, 45, 10]})

        counts = self.df["severity"].astype(str).str.upper().value_counts()
        valid_orders = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        filtered_counts = {k: int(counts.get(k, 0)) for k in valid_orders}
        return pd.DataFrame(list(filtered_counts.items()), columns=["Sévérité", "Nombre"])

    def get_temporal_evolution(self) -> pd.DataFrame:
        """Get time series trend of threats by date/month."""
        if self.df.empty or "published_date" not in self.df.columns:
            return pd.DataFrame({"Date": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"], "Menaces": [120, 150, 180, 210, 240, 290]})

        df_copy = self.df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["published_date"], errors="coerce")
        df_copy = df_copy.dropna(subset=["date"])

        if df_copy.empty:
            return pd.DataFrame({"Date": ["Jan 2025", "Fév 2025", "Mar 2025"], "Menaces": [100, 150, 200]})

        grouped = df_copy.groupby(df_copy["date"].dt.to_period("M")).size().reset_index(name="Menaces")
        grouped["Date"] = grouped["date"].astype(str)
        return grouped[["Date", "Menaces"]].tail(12)

    def get_top_threat_types(self) -> pd.DataFrame:
        """Get top threat types / attack vectors."""
        if self.df.empty or "threat_type" not in self.df.columns:
            return pd.DataFrame({"Type de Menace": ["RCE", "SQL Injection", "XSS", "Ransomware", "Auth Bypass"], "Occurrences": [85, 62, 44, 39, 28]})

        counts = self.df["threat_type"].dropna().value_counts().head(5).reset_index()
        counts.columns = ["Type de Menace", "Occurrences"]
        return counts

    def get_vulnerabilities_table(self, limit: int = 15) -> pd.DataFrame:
        """Get structured vulnerabilities table for display."""
        if self.df.empty:
            return pd.DataFrame()

        cols = [c for c in ["record_id", "severity", "threat_type", "affected_system", "cvss_score", "description"] if c in self.df.columns]
        table_df = self.df[cols].head(limit).copy()
        if "cvss_score" in table_df.columns:
            table_df["cvss_score"] = pd.to_numeric(table_df["cvss_score"], errors="coerce").fillna(0.0)
            table_df = table_df.sort_values(by="cvss_score", ascending=False)

        return table_df

    def get_priority_recommendations(self) -> List[Dict[str, str]]:
        """Get actionable security recommendations for travel sector."""
        return [
            {
                "title": "🔒 Sécurisation des API de Réservation & Billetterie",
                "detail": "Mettre en place une authentification OAuth2/JWT stricte avec limitation de débit (rate limiting) pour contrer les injections et accès non autorisés.",
            },
            {
                "title": "💳 Isolation des Passerelles de Paiement",
                "detail": "Garantir la conformité PCI-DSS v4.0 et isoler le réseau des transactions bancaires des serveurs web publics de l'agence.",
            },
            {
                "title": "🛡️ Filtrage WAF & Prévention DDoS",
                "detail": "Activer le pare-feu applicatif (WAF) avec règles d'inspection d'urgence sur les payloads RCE et XSS ciblés sur les formulaires voyageurs.",
            },
            {
                "title": "📋 Protection des Données Personnelles Voyageurs (PII)",
                "detail": "Chiffrer les données sensibles de passeport et de réservation au repos (AES-256) et en transit (TLS 1.3).",
            },
        ]

    def _init_synthetic_fallback(self) -> None:
        """Create fallback dataframe if parquet is unavailable."""
        self.df = pd.DataFrame(
            [
                {"record_id": f"CVE-2025-0{i}", "source": "CVE", "description": f"Vulnerability {i} in booking portal", "severity": "CRITICAL" if i % 3 == 0 else "HIGH", "threat_type": "RCE", "affected_system": "Booking API", "cvss_score": 9.8 - (i * 0.2)}
                for i in range(1, 50)
            ]
        )
