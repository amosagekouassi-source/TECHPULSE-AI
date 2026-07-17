# TECHPULSE-AI

TECHPULSE-AI is an AI-ready technology intelligence platform built from the
[GitHub Archive](https://www.gharchive.org/) event stream. It provides a clean,
modular ingestion foundation that downloads hourly archive files, streams their
contents safely, and normalizes useful event data for future analytics and AI
workflows.

> **Current status:** Sprint 2 focuses exclusively on GitHub Archive ingestion.

## Features

- Downloads hourly GitHub Archive `.json.gz` files.
- Creates the raw-data directory automatically when needed.
- Streams compressed JSON line by line without loading an entire archive into
  memory.
- Skips malformed JSON records safely and logs diagnostics.
- Extracts a consistent, AI-ready event schema.
- Uses dependency injection to keep pipeline components testable and decoupled.
- Includes unit tests for downloader, parser, extractor, and collector modules.

## Architecture

The ingestion pipeline follows single-responsibility and dependency-inversion
principles. Each component has one clear concern:

```text
GitHubArchiveCollector
        │
        ├── GitHubArchiveDownloader  → downloads an hourly .json.gz archive
        ├── GitHubArchiveParser      → yields parsed JSON events as a stream
        └── GitHubArchiveExtractor   → normalizes useful event fields
```

`GitHubArchiveCollector` orchestrates these components but does not duplicate
their logic. The resulting normalized events can later feed preprocessing,
embeddings, vector storage, analysis, and reporting modules.

## Installation

### Prerequisites

- Python 3.12 or later
- Git

### Clone and prepare the project

```bash
git clone https://github.com/amosagekouassi-source/TECHPULSE-AI.git
cd TECHPULSE-AI
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For testing and code-quality tools, install the development dependencies:

```bash
python -m pip install pytest ruff black
```

## Usage

Run the Sprint 2 integration check:

```bash
python main.py
```

The command downloads the configured GitHub Archive hourly file into `data/raw/`,
parses it, and displays the first ten normalized events.

Run the unit tests:

```bash
python -m pytest -q
```

Check style and formatting:

```bash
ruff check .
black --check .
```

Apply Black formatting when necessary:

```bash
black .
```

## Project Structure

```text
TECHPULSE-AI/
├── app/
│   ├── collector/                  # GitHub Archive ingestion pipeline
│   │   ├── downloader.py           # HTTP download of .json.gz archives
│   │   ├── parser.py               # Streaming gzip/JSON reader
│   │   ├── extractor.py            # Event-field normalization
│   │   └── github_archive.py       # Pipeline orchestrator
│   ├── preprocessing/              # Planned data-cleaning layer
│   ├── embeddings/                 # Planned embedding generation
│   ├── vector_store/               # Planned vector persistence
│   ├── analysis/                   # Planned intelligence analysis
│   ├── agent/                      # Planned AI agent layer
│   ├── reports/                    # Planned reporting layer
│   ├── dashboard/                  # Planned dashboard layer
│   └── utils/                      # Shared utilities
├── data/
│   ├── raw/                        # Downloaded GitHub Archive files
│   ├── processed/                  # Future processed datasets
│   └── vectors/                    # Future vector data
├── docs/                           # Project documentation
├── notebook/                       # Exploratory notebooks
├── tests/                          # Pytest unit tests
├── .env.example                    # Environment-variable template
├── main.py                         # Sprint 2 integration check
├── requirements.txt                # Runtime dependencies
├── README.md
└── LICENSE
```

## Tech Stack

- **Language:** Python 3.12+
- **HTTP client:** `requests`
- **Filesystem paths:** `pathlib`
- **Compressed data:** Python standard-library `gzip`
- **JSON parsing:** Python standard-library `json`
- **Testing:** `pytest`
- **Linting:** `ruff`
- **Formatting:** `black`
- **Version control:** Git and GitHub
- **Development environment:** VS Code

## Roadmap

- [x] Sprint 2 — GitHub Archive download, parsing, extraction, orchestration,
      and unit tests.
- [ ] Sprint 3 — Data preprocessing and event-quality validation.
- [ ] Sprint 4 — Embedding generation and vector-store integration.
- [ ] Sprint 5 — Technology trend analysis and anomaly detection.
- [ ] Sprint 6 — AI agent, reports, and interactive dashboard.

## License

This project is distributed under the [MIT License](LICENSE).
