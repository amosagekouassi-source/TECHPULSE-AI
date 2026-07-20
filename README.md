# TECHPULSE-AI

TECHPULSE-AI is an AI-powered cybersecurity assistant for travel agencies,
booking platforms, ticketing providers, and reservation systems. It collects,
preprocesses, and analyzes vulnerability and incident data to help travel-sector
teams understand cybersecurity risks and prioritize action.

> **Current status:** The project includes data ingestion, cybersecurity dataset
> preprocessing, and a CPU-compatible DistilBERT severity-classification module.
> GPU training through Google Colab and model hosting on Hugging Face Hub are the
> recommended next steps.

## Problem Statement

Travel agencies rely on booking engines, ticketing systems, online payments, and
customer-management tools. These interconnected systems can be affected by
security vulnerabilities, cyberattacks, and fraud attempts.

Many small and medium-sized travel organizations do not have a dedicated
cybersecurity team to continuously monitor emerging threats. TECHPULSE-AI is
designed to make threat information easier to collect, structure, classify, and
explore.

## Features

- GitHub Archive ingestion pipeline for technology intelligence data.
- NVD CVE preprocessing with dynamic CVSS v4.0, v3.1, and v3.0 metric support.
- Cybersecurity incident-dataset ingestion and schema unification.
- Unified TECHPULSE dataset exported as Parquet.
- JSON preprocessing report with record counts, severity distribution, and
  missing-value statistics.
- DistilBERT severity classifier for `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL`.
- CPU-compatible local training implementation.
- Modular architecture ready for Sentence Transformers, FAISS, RAG, LLMs, and
  Streamlit.

## Architecture

```text
Data Sources
├── NVD CVE feeds
├── Cybersecurity incident datasets
└── GitHub Archive
        │
        ▼
Collector → Preprocessing → DistilBERT Classifier → Embeddings
        → FAISS Vector Store → RAG → LLM → Streamlit Dashboard
```

## Project Structure

```text
TECHPULSE-AI/
├── app/
│   ├── collector/                  # GitHub Archive ingestion
│   ├── preprocessing/              # CVE and incident data preparation
│   ├── classifier/                 # DistilBERT severity classification
│   ├── embeddings/                 # Future Sentence Transformers layer
│   ├── vector_store/               # Future FAISS integration
│   ├── agent/                      # Future AI assistant layer
│   ├── reports/
│   ├── dashboard/                  # Future Streamlit application
│   └── utils/
├── data/
│   ├── raw/                        # Local source datasets, ignored by Git
│   └── processed/                  # Local Parquet and reports, ignored by Git
├── models/                          # Local trained models, ignored by Git
├── docs/
├── tests/
├── main.py                          # Preprocessing pipeline entry point
├── requirements.txt
├── README.md
└── LICENSE
```

## Installation

### Prerequisites

- Python 3.11 or later
- Git

```bash
git clone https://github.com/amosagekouassi-source/TECHPULSE-AI.git
cd TECHPULSE-AI
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Preprocessing Pipeline

Place the local datasets in the following paths:

```text
data/raw/cve/nvdcve-2.0-2025.json
data/raw/cve/nvdcve-2.0-2026.json
data/raw/incidents/cybersecurity_dataset.csv
data/raw/incidents/cybersecurity_synthesized_data.csv
```

Run preprocessing:

```bash
python main.py
```

Generated local artifacts:

```text
data/processed/techpulse_dataset.parquet
data/processed/preprocessing_report.json
```

## DistilBERT Severity Classifier

The classifier uses `distilbert-base-uncased` to predict a severity label from
a security description:

```text
LOW → 0
MEDIUM → 1
HIGH → 2
CRITICAL → 3
```

Run local CPU training:

```bash
python -m app.classifier.train
```

The trained model is saved locally in:

```text
models/distilbert_severity/
```

Run a prediction after training:

```bash
python -m app.classifier.predict "Remote code execution vulnerability in Apache"
```

Example output:

```json
{
  "severity": "CRITICAL",
  "confidence": 0.93
}
```

For faster training, use Google Colab with a GPU and publish the resulting
model and tokenizer to Hugging Face Hub.

## Technology Stack

- Python 3.11+
- pandas and PyArrow
- PyTorch and Transformers
- scikit-learn
- requests
- Planned: Sentence Transformers, FAISS, Gemini/OpenAI, and Streamlit

## Roadmap

- [x] GitHub Archive collector.
- [x] CVE and incident preprocessing pipeline.
- [x] Unified Parquet dataset and preprocessing report.
- [x] DistilBERT severity-classifier implementation.
- [ ] GPU training notebook for Google Colab.
- [ ] Hugging Face Hub model publishing and remote loading.
- [ ] Sentence Transformer embeddings and FAISS vector store.
- [ ] Retrieval-Augmented Generation pipeline.
- [ ] Gemini/OpenAI integration.
- [ ] Streamlit cybersecurity dashboard.

## Data and Model Policy

Raw datasets, generated Parquet files, and trained model artifacts are kept
local and excluded from Git. This prevents oversized files from blocking GitHub
pushes and keeps the source repository lightweight.

## License

This project is distributed under the [MIT License](LICENSE).
