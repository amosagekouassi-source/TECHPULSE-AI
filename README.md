# TECHPULSE-AI

Assistant intelligent de cybersécurité pour les agences de voyage

TECHPULSE-AI se concentre sur la cybersécurité des agences de voyage, des
plateformes de billetterie et des systèmes de réservation. Le projet collecte
et normalise des données de vulnérabilités et d’incidents pour proposer des
alertes, des classements de risque et un assistant IA adapté aux besoins du
secteur du voyage.

> **Current status:** Le projet a évolué vers un assistant de cybersécurité
> pour les PME du voyage, avec un pipeline d’ingestion, un prétraitement de
> données, une classification de sévérité et une intégration Hugging Face.

## 1. Problématique

Les agences de voyage utilisent quotidiennement des systèmes de réservation,
des plateformes de billetterie, des solutions de paiement en ligne et des
outils de gestion des clients. Ces technologies sont exposées à des
vulnérabilités de sécurité, des cyberattaques et des tentatives de fraude.

La majorité des petites et moyennes agences ne disposent pas d’une équipe
spécialisée en cybersécurité capable de surveiller en permanence les nouvelles
menaces. Une faille non détectée ou une attaque réussie peut entraîner des
pertes financières, une interruption de service et une atteinte à la réputation
de l’entreprise.

## 2. Solution Proposée

TECHPULSE-AI est un assistant intelligent de cybersécurité conçu spécialement
pour les agences de voyage.

La plateforme collecte et analyse automatiquement les informations de sécurité
provenant de sources fiables afin d’identifier les menaces pouvant affecter les
systèmes de réservation et de billetterie.

Grâce à l’intelligence artificielle, elle fournit des alertes, des
recommandations de correction et un assistant conversationnel permettant aux
utilisateurs de comprendre rapidement les risques et les actions à entreprendre.

## 3. Objectifs

- Surveiller les vulnérabilités affectant les technologies utilisées dans le
  secteur du voyage.
- Fournir des alertes de sécurité pertinentes.
- Aider les agences à mieux comprendre les risques auxquels elles sont exposées.
- Générer des recommandations de correction adaptées.
- Simplifier l’accès aux informations de cybersécurité grâce à l’intelligence
  artificielle.

## 4. Utilisateurs Cibles

- Agences de voyage
- Agences de billetterie
- Responsables informatiques
- Administrateurs systèmes
- Responsables de la sécurité informatique
- Gestionnaires de plateformes de réservation

## 5. Fonctionnalités MVP

- Surveillance des vulnérabilités de sécurité.
- Classification automatique des risques.
- Recherche intelligente dans les données de cybersécurité.
- Assistant IA conversationnel.
- Tableau de bord de suivi des menaces.
- Recommandations de correction.

## 6. Fonctionnalités Futures

- Alertes de sécurité en temps réel.
- Analyse des incidents récents du secteur du voyage.
- Analyse des risques de fraude liés à la billetterie.
- Historique des vulnérabilités surveillées.
- Génération automatique de rapports de sécurité.
- Recommandations de prévention contre la fraude.
- Détection intelligente des comportements suspects.

## 7. Architecture Technique

1. Collecte des données via des API de cybersécurité et des flux publics.
2. Nettoyage et prétraitement des données.
3. Classification des vulnérabilités à l’aide de modèles NLP.
4. Génération d’embeddings vectoriels.
5. Stockage dans une base vectorielle FAISS.
6. Recherche sémantique et système RAG.
7. Génération de réponses via un assistant IA.
8. Visualisation dans un tableau de bord interactif.

## 8. Technologies Utilisées

- Python
- APIs
- JSON
- NLP (Traitement Automatique du Langage Naturel)
- Vector Embeddings
- FAISS
- Retrieval-Augmented Generation (RAG)
- Transformers
- Machine Learning Supervisé
- Feature Engineering

## 9. Valeur Ajoutée

TECHPULSE-AI permet aux agences de voyage d’accéder à une expertise
cybersécurité sans disposer d’une équipe spécialisée. La solution centralise les
informations critiques, simplifie l’analyse des menaces et aide les entreprises à
prendre rapidement les bonnes décisions pour protéger leurs activités et leurs
clients.

## 10. Vision à Long Terme

Faire de TECHPULSE-AI une plateforme de référence pour la cybersécurité des
agences de voyage, capable de surveiller les menaces, anticiper les risques de
fraude, assister les équipes métier et renforcer la sécurité des systèmes de
réservation et de billetterie.

## Installation

### Prérequis

- Python 3.12 ou plus récent
- Git

### Préparer le projet

```bash
git clone https://github.com/amosagekouassi-source/TECHPULSE-AI.git
cd TECHPULSE-AI
python -m venv venv
```

Windows PowerShell :

```powershell
.\venv\Scripts\Activate.ps1
```

macOS/Linux :

```bash
source venv/bin/activate
```

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Entraînement et déploiement sur Google Colab

Ce projet supporte l’entraînement sur Colab et le déploiement sur Hugging Face
Hub. Le script `app/classifier/train.py` accepte désormais les options
`--push-to-hub` et `--hub-model-id`.

### Exemple Colab

```python
!pip install -q -U pip
!pip install -q -r requirements.txt
```

```python
from huggingface_hub import login
login(token="YOUR_HF_TOKEN")
```

```bash
python app/classifier/train.py \
  --dataset-path /path/to/techpulse_dataset.parquet \
  --model-output-dir /content/models/distilbert_severity \
  --model-name distilbert-base-uncased \
  --epochs 3 \
  --batch-size 16 \
  --push-to-hub \
  --hub-model-id YOUR_HF_USERNAME/techpulse-distilbert
```

### Utilisation locale d’un modèle Hugging Face

```bash
python app/classifier/predict.py "Texte de vulnérabilité" \
  --model-source YOUR_HF_USERNAME/techpulse-distilbert
```

## Project Structure

```text
TECHPULSE-AI/
├── app/
│   ├── classifier/                # Classification DistilBERT et prédiction
│   ├── collector/                 # Pipeline d’ingestion GitHub Archive
│   ├── preprocessing/             # Nettoyage et mappage des sources
│   ├── embeddings/                # Génération d’embeddings
│   ├── vector_store/              # Persistance vectorielle
│   ├── analysis/                  # Analyse des menaces
│   ├── agent/                     # Assistant IA conversationnel
│   ├── reports/                   # Rapports de sécurité
│   └── dashboard/                 # Visualisation des menaces
├── data/
│   ├── raw/
│   ├── processed/
│   └── vectors/
├── docs/
├── notebook/
├── tests/
├── main.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Commandes utiles

- `python main.py` — exécute le pipeline de prétraitement.
- `python app/classifier/train.py` — entraîne DistilBERT localement ou sur Colab.
- `python app/classifier/predict.py` — prédit la sévérité d’une description.
- `python -m pytest -q` — lance les tests.

## Licence

Ce projet est distribué sous la licence MIT.
