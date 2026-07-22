# TECHPULSE-AI

TECHPULSE-AI is an AI-powered cybersecurity assistant and continuous monitoring platform for travel agencies, booking platforms, ticketing providers, and reservation systems. It automatically collects, preprocesses, and analyzes vulnerability (CVE) and incident data to help travel-sector teams understand cybersecurity risks and prioritize action in real-time.

> **Current status:** The project features a fully operational, real-time National Vulnerability Database (NVD) monitoring pipeline, a FAISS-backed Retrieval-Augmented Generation (RAG) assistant powered by Gemini (or OpenAI fallback offline mode), a DistilBERT severity classification module, and a unified executive dashboard frontend.

## Problem Statement

Travel agencies rely on booking engines, ticketing systems, online payments, and customer-management tools. These interconnected systems (e.g., Amadeus, Sabre, GDS, PCI-DSS compliance gateways) handle highly sensitive data (passports, credit cards) and can be affected by security vulnerabilities, cyberattacks, and fraud attempts.

Many small and medium-sized travel organizations do not have a dedicated cybersecurity team to continuously monitor emerging threats. TECHPULSE-AI is designed to automatically filter ambient noise, assess vulnerability criticality, and provide immediately actionable recommendations in natural language before any financial or reputational damage occurs.

## Features

- **Real-Time NVD Monitoring Pipeline:** Continuous ingestion of new CVEs via the NIST NVD API v2 using delta filtering and pagination.
- **APScheduler Background Jobs:** Automatic data polling (default every 6 hours) running seamlessly in the background.
- **Dynamic Dataset Updation:** Automatically merges new CVEs into the local Parquet dataset and triggers on-the-fly FAISS vector index rebuilds.
- **Intent-Driven RAG Assistant:** An advanced conversational AI (powered by Gemini) with a deterministic Intent Router (General Conversation, Global Reports, Cyber Threats).
- **DistilBERT Severity Classifier:** Automatic severity labeling (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) using `distilbert-base-uncased`.
- **Offline Template Engine Fallback:** A robust offline fallback ensures the platform remains partially functional even if the LLM API is rate-limited or revoked.
- **Streamlit & React Dashboard:** Unified frontend platform for executive reporting, chatting with the AI, and visualizing key risk metrics.

## Architecture

```text
Data Sources
├── NVD CVE feeds (Real-time API v2)
├── Cybersecurity incident datasets
└── GitHub Archive
        │
        ▼ (Scheduled Polling via APScheduler)
NVDCollector → DatasetUpdater (Merge) → DistilBERT Classifier 
        │
        ▼
techpulse_dataset.parquet → FAISS Vector Store 
        │
        ▼ (Intent Routing)
RAG Pipeline → Gemini LLM (or Offline Fallback)
        │
        ▼
Unified Dashboard (Streamlit / React Frontend)
```

## Project Structure

```text
TECHPULSE-AI/
├── app/
│   ├── agent/                      # RAG and Conversational Pipeline core
│   ├── analytics/                  # KPIs, scoring, and data analytics engine
│   ├── classifier/                 # DistilBERT severity classification
│   ├── collector/                  # NVD API v2, GitHub Archive ingestion & APScheduler
│   ├── dashboard/                  # Streamlit application
│   ├── embeddings/                 # Sentence Transformers layer
│   ├── llm/                        # LLM client (Gemini/OpenAI) with Intent prompting
│   ├── rag/                        # 3-Intent deterministic Router
│   ├── reports/                    # Document/PDF report generation
│   ├── vector_store/               # FAISS integration
│   └── utils/
├── data/
│   ├── raw/                        # Local source datasets, ignored by Git
│   └── processed/                  # Local Parquet and reports, ignored by Git
├── frontend/                       # Modern React web app UI
├── models/                         # Local trained models, ignored by Git
├── scripts/
│   ├── run_collector.py            # CLI for manual NVD collection
│   └── start_monitoring.py         # Entry point for full monitoring & dashboard
├── main.py                         # Legacy preprocessing pipeline entry point
├── requirements.txt
├── README.md
└── LICENSE
```

## Installation

### Prerequisites

- Python 3.11 or later
- Git
- Node.js & npm (for frontend)

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

### Environment Variables

Create a `.env` file in the root directory:

```env
# Required for natural language generation
GEMINI_API_KEY=your_gemini_api_key

# Optional: Speeds up NVD collection (50 req/30s vs 5 req/30s)
NVD_API_KEY=your_nvd_api_key
```

## Usage

### 1. Full Monitoring Platform (Recommended)

Start the APScheduler background job (polls NVD every 6 hours) and the Streamlit dashboard simultaneously:

```bash
python scripts/start_monitoring.py
```

*The dashboard will be available at `http://localhost:8501`.*

### 2. Manual NVD Collection

Trigger an immediate CVE collection from the NVD API manually:

```bash
python scripts/run_collector.py --hours 24
```

*Options:*
- `--hours 48` : Collect last 48 hours.
- `--start 2025-01-01` : Collect since a specific date.

### 3. DistilBERT Severity Classifier

Run local CPU training:

```bash
python -m app.classifier.train
```

Run a prediction after training:

```bash
python -m app.classifier.predict "Remote code execution vulnerability in Apache"
```

## Technology Stack

- **Backend:** Python 3.11+, APScheduler, pandas, PyArrow, requests
- **AI / ML:** PyTorch, Transformers, sentence-transformers, scikit-learn, FAISS
- **LLM:** Google Gemini (`gemini-2.0-flash`) via `google-genai`
- **Frontend:** Streamlit, React, Vite, Tailwind CSS

## Data and Model Policy

Raw datasets, generated Parquet files, `node_modules`, and trained model artifacts are kept local and excluded from Git. This prevents oversized files from blocking GitHub pushes and keeps the source repository lightweight.

## License

This project is distributed under the [MIT License](LICENSE).
