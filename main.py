"""Run the TECHPULSE-AI V2 preprocessing and dataset fusion pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from app.preprocessing.cve_preprocessor import CvePreprocessor
from app.preprocessing.dataset_builder import DatasetBuilder
from app.preprocessing.incident_preprocessor import IncidentPreprocessor

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
CVE_2025_PATH = PROJECT_ROOT / "data" / "raw" / "cve" / "nvdcve-2.0-2025.json"
CVE_2026_PATH = PROJECT_ROOT / "data" / "raw" / "cve" / "nvdcve-2.0-2026.json"
INCIDENT_DATASET_1_PATH = (
    PROJECT_ROOT / "data" / "raw" / "incidents" / "cybersecurity_dataset.csv"
)
INCIDENT_DATASET_2_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "incidents"
    / "cybersecurity_synthesized_data.csv"
)
PROCESSED_DIRECTORY = PROJECT_ROOT / "data" / "processed"
DATASET_OUTPUT_PATH = PROCESSED_DIRECTORY / "techpulse_dataset.parquet"
REPORT_OUTPUT_PATH = PROCESSED_DIRECTORY / "preprocessing_report.json"


def configure_logging() -> None:
    """Configure console logging for the preprocessing pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def resolve_incident_dataset_2_path() -> Path:
    """Resolve the configured synthesized dataset path with local compatibility.

    Returns:
        The requested dataset path when it exists; otherwise, the existing local
        filename used during early project setup.
    """
    if INCIDENT_DATASET_2_PATH.is_file():
        return INCIDENT_DATASET_2_PATH

    legacy_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "incidents"
        / "cybersecurity synthesized data (1).csv"
    )
    if legacy_path.is_file():
        LOGGER.warning(
            "Using legacy synthesized dataset filename %s; rename it to %s when possible.",
            legacy_path.name,
            INCIDENT_DATASET_2_PATH.name,
        )
        return legacy_path

    return INCIDENT_DATASET_2_PATH


def main() -> int:
    """Build the unified TECHPULSE dataset and its preprocessing report.

    Returns:
        Zero when all artifacts are generated successfully, otherwise one.
    """
    configure_logging()
    LOGGER.info("Starting TECHPULSE-AI V2 preprocessing pipeline")

    cve_preprocessor = CvePreprocessor()
    incident_preprocessor = IncidentPreprocessor()
    dataset_builder = DatasetBuilder()

    try:
        cve_2025 = cve_preprocessor.preprocess(CVE_2025_PATH)
        cve_2026 = cve_preprocessor.preprocess(CVE_2026_PATH)
        incident_dataset_1 = incident_preprocessor.load_dataset_1(
            INCIDENT_DATASET_1_PATH
        )
        incident_dataset_2 = incident_preprocessor.load_dataset_2(
            resolve_incident_dataset_2_path()
        )

        unified_dataset = dataset_builder.build(
            cve_2025=cve_2025,
            cve_2026=cve_2026,
            incident_dataset_1=incident_dataset_1,
            incident_dataset_2=incident_dataset_2,
        )
        dataset_builder.save_dataset(unified_dataset, DATASET_OUTPUT_PATH)
        report = dataset_builder.generate_report(unified_dataset, REPORT_OUTPUT_PATH)

        LOGGER.info(
            "Pipeline completed: %d records written to %s",
            report["total_records"],
            DATASET_OUTPUT_PATH,
        )
        return 0
    except (FileNotFoundError, ValueError, OSError, ImportError) as error:
        LOGGER.error("Preprocessing pipeline failed: %s", error)
        return 1
    except Exception:
        LOGGER.exception("Preprocessing pipeline failed unexpectedly")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
