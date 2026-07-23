# 🛡️ TECHPULSE-AI — Cyber Intelligence & RAG Platform for Travel Tech

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![React](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-61dafb)
![Render](https://img.shields.io/badge/Backend-Live%20on%20Render-informational)
![Vercel](https://img.shields.io/badge/Frontend-Live%20on%20Vercel-black)

**TECHPULSE-AI** is an AI-powered SaaS cyber intelligence and continuous threat monitoring platform designed specifically for the travel sector (airports, travel agencies, reservation engines, and GDS software like Amadeus & Sabre).

It automatically ingests, filters, and analyzes vulnerability data (NVD CVEs), classifies threat severities locally via DistilBERT, and provides a resilient conversational RAG agent (Gemini 2.0 + Groq LLaMA 3.3 70B Fallback).

---

## 🌐 Live Deployments

- 🎨 **Frontend (React UI) :** [https://techpulse-ai-seven.vercel.app](https://techpulse-ai-seven.vercel.app)
- ⚙️ **Backend API (FastAPI) :** [https://techpulse-ai-sm13.onrender.com](https://techpulse-ai-sm13.onrender.com)

---

## 🚀 Key Features

- **Automated NVD Ingestion Pipeline:** Fetches and cleans real-time CVE vulnerabilities from the NIST NVD API v2, filtering travel-related infrastructure (Amadeus, Sabre, Galileo, PCI-DSS).
- **Resilient Multi-LLM RAG Engine:** 
  - Uses `all-MiniLM-L6-v2` embeddings with a **FAISS** vector store for fast, semantic context retrieval.
  - Features an **automatic multi-key rotation** (5 Gemini API keys) with seamless **fallback to Groq LLaMA-3.3-70B** in case of quota depletion (99.9% uptime).
- **DistilBERT Severity Classifier:** Supervised local Machine Learning model (`distilbert-base-uncased`) trained to classify threat levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Deterministic Intent Router:** Protects the agent against prompt injection and off-topic queries by routing user messages to specific pipelines (`GENERAL_QUESTION`, `GLOBAL_REPORT`, `CYBER_THREAT`).
- **Modern Executive Dashboard:** React/Vite frontend with dark mode glassmorphism UI, real-time threat KPIs, and RAG Chatbot.

---

## 🏗️ System Architecture

```text
               +----------------------------------+
               |  NIST National Vulnerability     |
               |       Database (NVD API v2)      |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |  nvd_collector.py (Filtering)    |
               +----------------------------------+
                                |
        +-----------------------+-----------------------+
        |                                               |
        v                                               v
+-----------------------+               +-------------------------------+
| DistilBERT Classifier |               | SentenceTransformers (MiniLM) |
| (Severity Prediction) |               +-------------------------------+
+-----------------------+                               |
                                                        v
                                                +---------------+
                                                |  FAISS Index  |
                                                +---------------+
                                                        |
                                                        v
+-----------------------+                       +---------------+
| React Frontend UI     | <===================> | FastAPI Server|
| (Deployed on Vercel)  |    REST HTTP API      | (on Render)   |
+-----------------------+                       +---------------+
                                                        |
                                                        v
                                        +-------------------------------+
                                        | Multi-LLM Fallback Engine     |
                                        | 1. Gemini 2.0 Flash (Rotation)|
                                        | 2. Groq LLaMA 3.3 70B (Relay) |
                                        +-------------------------------+
```

---

## 📁 Repository Structure

```text
TECHPULSE-AI/
├── app/
│   ├── agent/                      # RAG and Conversational Pipeline core
│   ├── analytics/                  # KPIs and scoring engine
│   ├── classifier/                 # DistilBERT supervised fine-tuning & evaluation
│   ├── collector/                  # NVD API v2 ingestion scripts
│   ├── embeddings/                 # SentenceTransformers (MiniLM) vectorizer
│   ├── llm/                        # Multi-LLM client (Gemini & Groq Fallback)
│   ├── rag/                        # Intent Router & FAISS Retriever
│   └── vector_store/               # FAISS index management
├── frontend/                       # React / Vite / Tailwind UI source code
├── scripts/
│   └── run_collector.py            # CLI for manual CVE collection
├── server.py                       # FastAPI production entry point
├── requirements.txt                # Python dependencies
└── README.md
```

---

## 🛠️ Local Installation & Development

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18+ (for frontend development)

### 2. Clone & Setup Backend
```bash
git clone https://github.com/amosagekouassi-source/TECHPULSE-AI.git
cd TECHPULSE-AI

# Create virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables Setup
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
PORT=8000
```

### 4. Run Backend Server locally
```bash
python server.py
```
*Server will start at `http://127.0.0.1:8000`.*

### 5. Run Frontend locally
```bash
cd frontend
npm install
npm run dev
```
*Frontend will be accessible at `http://localhost:5173`.*

---

## 🧪 Model Training & Evaluation

To train the DistilBERT severity classification model locally:

```bash
python -m app.classifier.train
```

Evaluation metrics (Accuracy, Precision, Recall, F1-Score) and confusion matrix artifacts will be exported to `models/training_metrics.json`.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.
