# 🛡️ TECHPULSE-AI — Intelligence Cyber & Sécurité du Voyage

<div align="center">

[![Vercel](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://techpulse-ai-seven.vercel.app)
[![Render](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://techpulse-ai-sm13.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Plateforme SaaS d'intelligence cyber dédiée au secteur du voyage (GDS Amadeus, Sabre, Galileo).**

[🚀 Demo Live](https://techpulse-ai-seven.vercel.app) · [📖 Documentation API](https://techpulse-ai-sm13.onrender.com/docs) · [📊 Rapport d'avancement](rapport_avancement.md)

</div>

---

## ✨ Présentation

**TECHPULSE-AI** est une plateforme de veille cyber spécialisée pour les agences de voyage utilisant des systèmes GDS (Global Distribution Systems) comme **Amadeus**, **Sabre** et **Galileo**. Ces systèmes manipulent des données sensibles (passeports, cartes bancaires) et constituent des cibles privilégiées.

La plateforme automatise la surveillance des CVE/CVSS, fournit des recommandations actionnables via un assistant RAG, et garantit une **haute disponibilité** grâce à un système de fallback multi-LLM.

---

## 🏗️ Architecture Technique

```
┌─────────────────────────────────────────────────────────────────┐
│                        TECHPULSE-AI                             │
│                                                                  │
│  ┌────────────────────┐          ┌──────────────────────────┐   │
│  │   Frontend React   │  HTTPS   │   Backend FastAPI         │   │
│  │   (Vercel CDN)     │◄────────►│   (Render Cloud)         │   │
│  │                    │          │                           │   │
│  │  • Dashboard       │          │  ┌─────────────────────┐ │   │
│  │  • Chatbot RAG     │          │  │   RAG Pipeline       │ │   │
│  │  • GDS Monitor     │          │  │                       │ │   │
│  │  • i18n (FR/EN)    │          │  │  Query → FAISS Search │ │   │
│  └────────────────────┘          │  │  → Gemini/Groq LLM   │ │   │
│                                  │  └─────────────────────┘ │   │
│                                  │                           │   │
│                                  │  ┌─────────────────────┐ │   │
│                                  │  │  DistilBERT         │ │   │
│                                  │  │  (Severity Classifier)│ │   │
│                                  │  └─────────────────────┘ │   │
│                                  │                           │   │
│                                  │  ┌─────────────────────┐ │   │
│                                  │  │  SQLite DB           │ │   │
│                                  │  │  (Chat History)      │ │   │
│                                  │  └─────────────────────┘ │   │
│                                  └──────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LLM Fallback Chain                          │    │
│  │  Gemini Key 1 → Key 2 → Key 3 → Key 4 → Key 5 → Groq   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Fonctionnalités Clés

| Fonctionnalité | Description | Technologie |
|---|---|---|
| 🤖 **Assistant RAG** | Chatbot cyber avec contexte vectoriel | FAISS + Gemini 2.0 Flash |
| 🧠 **Classification IA** | Sévérité des CVE sans coût API | DistilBERT (Fine-tuné) |
| 🔄 **Fallback Multi-LLM** | Rotation 5 clés Gemini + Groq | Python + Groq SDK |
| 🌐 **Monitoring GDS** | Surveillance APIs Amadeus/Sabre/Galileo | React + Simulation Live |
| 📊 **Dashboard Exécutif** | KPIs, graphiques de menaces, rapports PDF | Recharts |
| 🌍 **Bilingue FR/EN** | Interface complète en 2 langues | i18n React |
| 💾 **Persistance** | Historique des chats conservé | SQLite |
| 📋 **Export PDF** | Rapport d'audit téléchargeable | Vanilla JS Blob |

---

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.11+
- Node.js 18+ (pour le dev Vite)
- Clé API Google Gemini (gratuite sur [aistudio.google.com](https://aistudio.google.com/apikey))
- Clé API Groq (gratuite sur [console.groq.com](https://console.groq.com))

### 1. Cloner le projet

```bash
git clone https://github.com/votre-username/techpulse-ai.git
cd techpulse-ai
```

### 2. Configurer l'environnement backend

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos clés
# GEMINI_API_KEY=AIza...
# GROQ_API_KEY=gsk_...
```

### 3. Lancer le Backend FastAPI

```bash
# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Démarrer le serveur
python server.py
# → API disponible sur http://localhost:8000
# → Documentation interactive : http://localhost:8000/docs
```

### 4. Lancer le Frontend

**Option A — Fichier HTML standalone (simple, sans build)**
```bash
# Ouvrir directement dans le navigateur
start frontend/index.html
```

**Option B — Serveur de développement Vite**
```bash
cd frontend
npm install
npm run dev
# → Disponible sur http://localhost:3000
```

---

## 🌐 Déploiement en Production

### Frontend → Vercel

1. Connecter le repo GitHub à [vercel.com](https://vercel.com)
2. Répertoire de déploiement : `frontend/`
3. Fichier de sortie : `index.html`
4. **URL de production** : [https://techpulse-ai-seven.vercel.app](https://techpulse-ai-seven.vercel.app)

### Backend → Render

1. Connecter le repo GitHub à [render.com](https://render.com)
2. Type : **Web Service** (Python)
3. Build command : `pip install -r requirements.txt`
4. Start command : `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Configurer les variables d'environnement (`GEMINI_API_KEY`, `GROQ_API_KEY`, etc.)

---

## 📁 Structure du Projet

```
TECHPULSE-AI/
├── server.py                   # API FastAPI principale
├── main.py                     # Point d'entrée alternatif
├── requirements.txt            # Dépendances Python
├── .env.example                # Template de configuration
├── render.yaml                 # Configuration Render
├── vercel.json                 # Configuration Vercel
│
├── app/                        # Modules backend
│   ├── agent/                  # Agent conversationnel
│   ├── classifier/             # DistilBERT (Fine-tuning sévérité)
│   ├── collector/              # Collecteur NVD CVE
│   ├── embeddings/             # Génération embeddings MiniLM
│   ├── llm/                    # Gestion multi-LLM + fallback
│   ├── rag/                    # Pipeline RAG complet
│   └── vector_store/           # Interface FAISS
│
├── models/
│   └── vector_store/           # Index FAISS (base vectorielle)
│
├── frontend/
│   ├── index.html              # 🎯 App standalone (Production)
│   └── src/                    # Code source Vite (Développement)
│       ├── App.jsx
│       ├── components/
│       │   ├── ChatbotTab.jsx
│       │   ├── DashboardTab.jsx
│       │   ├── GdsSecurityTab.jsx
│       │   ├── Header.jsx
│       │   ├── Sidebar.jsx
│       │   └── SettingsTab.jsx
│       └── i18n/
│           └── translations.js # Traductions FR/EN
│
├── data/                       # Données CVE brutes
├── notebooks/                  # Notebooks d'analyse & fine-tuning
├── tests/                      # Tests unitaires
│   ├── test_router.py
│   └── test_pipeline.py
│
└── docs/                       # Documentation technique
```

---

## 🧪 Tests

```bash
# Tester le routeur d'intentions
python -m pytest test_router.py -v

# Tester le pipeline RAG
python -m pytest test_pipeline.py -v

# Vérifier que le serveur démarre
python -c "from server import app; print('✓ Server OK')"
```

---

## 🔒 Système de Résilience (Fallback LLM)

```python
# Ordre de priorité dans call_llm()
1. GEMINI_API_KEY    (Projet GCP 1 — Clé principale)
2. GEMINI_API_KEY_2  (Projet GCP 2 — Quota indépendant)
3. GEMINI_API_KEY_3  (Projet GCP 3 — Quota indépendant)
4. GEMINI_API_KEY_4  (Projet GCP 2 — Clé secondaire)
5. GEMINI_API_KEY_5  (Projet GCP 1 — Clé secondaire)
6. GROQ_API_KEY      → LLaMA 3.3 70B (Fallback final)
```

Si toutes les clés Gemini renvoient HTTP 429 (quota épuisé), le système bascule **automatiquement** sur Groq en moins d'1 seconde, garantissant 99.9% de disponibilité.

---

## 📊 Données & Base Vectorielle

Les CVE utilisées par le RAG proviennent de l'**API NVD (National Vulnerability Database)** du NIST, filtrées sur les mots-clés du secteur voyage (Amadeus, Sabre, Galileo, GDS, PNR).

```bash
# Reconstruire la base vectorielle FAISS depuis les données NVD
python -m app.collector.nvd_collector
python -m app.embeddings.build_index
```

---

## 👥 Crédits & Stack Technologique

| Couche | Technologie |
|---|---|
| LLM Principal | Google Gemini 2.0 Flash |
| LLM Fallback | Groq LLaMA 3.3 70B |
| Embeddings | SentenceTransformers `all-MiniLM-L6-v2` (384 dim) |
| Recherche Sémantique | FAISS (Meta AI) |
| Classification | DistilBERT (Fine-tuné sur dataset CVE/CVSS) |
| Backend | FastAPI + Uvicorn + SQLite |
| Frontend | React 18 + Tailwind CSS |
| Déploiement | Vercel (frontend) + Render (backend) |
| Source CVE | NIST NVD API v2.0 |

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

<div align="center">
  <strong>TECHPULSE-AI</strong> — Développé dans le cadre d'un projet académique · 2026
</div>
