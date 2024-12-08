# Guide du Développeur : Interface Ollama avec Gradio 🤖

## Introduction aux Large Language Models (LLMs)

Salut Paul ! En tant que développeur, tu vas découvrir comment intégrer des modèles de langage dans tes applications. Les LLMs sont des réseaux de neurones basés sur l'architecture Transformer, capables de comprendre et générer du langage naturel via des mécanismes d'attention.

### Architecture Technique
- **Frontend**: Interface utilisateur construite avec Gradio
- **Backend**: Serveur Ollama local pour l'inférence des modèles
- **API**: Communication via REST API pour le streaming des réponses
- **Modèles**: Support des modèles Llama2, Mistral, et autres architectures compatibles

## Prérequis Techniques

1. **Python 3.12+**
   ```bash
   python --version
   # Doit retourner Python 3.12.x ou supérieur
   ```

2. **Ollama**: Serveur d'inférence local
   - [Documentation API](https://github.com/ollama/ollama/blob/main/docs/api.md)
   - Binaires disponibles :
     - [macOS (arm64/amd64)](https://ollama.ai/download/mac)
     - [Windows (amd64)](https://ollama.ai/download/windows)
     - [Linux (amd64)](https://ollama.ai/download/linux)
   
   Installation et vérification :
   ```bash
   # macOS/Linux
   curl https://ollama.ai/install.sh | sh
   
   # Vérification de l'API
   curl http://localhost:11434/api/tags
   ```

3. **UV**: Package Manager Rust-based
   ```bash
   # Installation
   pip install uv
   
   # Comparaison des performances
   time uv pip install numpy
   time pip install numpy
   ```

## Gestion d'Environnement Python

### Comparaison des Solutions

1. **UV (Recommandé)**
   ```bash
   # Installation
   pip install uv
   
   # Création environnement
   uv venv
   
   # Installation rapide des dépendances
   time uv pip install -r requirements.txt  # 2-3x plus rapide que pip
   
   # Avantages
   - ✅ Performance : Écrit en Rust, 2-3x plus rapide que pip
   - ✅ Résolution déterministe des dépendances
   - ✅ Compatible avec pip et pyproject.toml
   - ✅ Isolation complète des dépendances
   - ❌ Projet récent, moins mature que les alternatives
   ```

2. **venv (Standard Python)**
   ```bash
   # Création environnement
   python -m venv .venv
   
   # Installation des dépendances
   pip install -r requirements.txt
   
   # Avantages
   - ✅ Inclus dans Python standard
   - ✅ Léger et simple
   - ✅ Parfaite isolation
   - ❌ Lent pour l'installation des packages
   - ❌ Pas d'outils avancés de gestion des dépendances
   ```

3. **Conda (Data Science)**
   ```bash
   # Installation Miniconda
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
   bash Miniconda3-latest-MacOSX-arm64.sh
   
   # Création environnement
   conda create -n ollama-env python=3.12
   conda activate ollama-env
   
   # Installation des dépendances
   conda install --file requirements.txt
   
   # Avantages
   - ✅ Gestion des dépendances non-Python (CUDA, C++)
   - ✅ Popular dans la communauté Data Science
   - ✅ Environnements reproductibles
   - ❌ Plus lourd que venv
   - ❌ Peut être lent pour la résolution des dépendances
   ```

4. **Poetry (Production)**
   ```bash
   # Installation
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Initialisation projet
   poetry init
   
   # Installation dépendances
   poetry install
   
   # Avantages
   - ✅ Gestion complète du cycle de vie des packages
   - ✅ Résolution déterministe des dépendances
   - ✅ Build et publication de packages
   - ❌ Courbe d'apprentissage plus raide
   - ❌ Peut être lent sur de gros projets
   ```

### Pourquoi UV pour ce Projet ?

1. **Performance**
   ```bash
   # Benchmark installation
   time uv pip install -r requirements.txt
   time pip install -r requirements.txt
   time poetry install
   time conda install --file requirements.txt
   ```

2. **Compatibilité**
   ```toml
   # pyproject.toml
   [project]
   name = "ollama-gradio-webui"
   version = "0.1.0"
   dependencies = [
       "gradio==4.44.1",
       "ollama==0.1.6",
   ]
   
   [tool.uv]
   pip = true  # Active la compatibilité pip
   ```

3. **Workflow Développement**
   ```bash
   # Création environnement propre
   uv venv --reset
   source .venv/bin/activate
   
   # Installation rapide
   uv pip install -r requirements.txt
   
   # Ajout dépendance
   uv pip install pandas
   uv pip freeze > requirements.txt
   
   # Clean cache si nécessaire
   uv cache clean
   ```

4. **Intégration CI/CD**
   ```yaml
   # .github/workflows/test.yml
   steps:
     - uses: actions/checkout@v3
     - uses: actions/setup-python@v4
       with:
         python-version: '3.12'
     - run: pip install uv
     - run: uv venv
     - run: uv pip install -r requirements.txt
     - run: python -m pytest
   ```

## Configuration du Projet

### 1. Setup du Repository
```bash
git clone https://github.com/Vinh-thuy/ollama-gradio-webui.git
cd ollama-gradio-webui
```

### 2. Environnement Virtuel avec UV
```bash
uv venv
source .venv/bin/activate  # Unix
.venv\\Scripts\\activate   # Windows
```

### 3. Gestion des Dépendances
```bash
# Installation avec UV (plus rapide que pip)
uv pip install -r requirements.txt

# Dépendances principales :
# - gradio==4.44.1: Framework UI
# - ollama==0.1.6: Client API Ollama
# - fastapi: Serveur ASGI
# - uvicorn: Serveur d'application ASGI
```

### 4. Configuration des Modèles
```bash
# Pull d'un modèle (exemple avec llama2)
ollama pull llama2

# Liste des modèles et leurs tailles
ollama list

# Vérification des capacités GPU
nvidia-smi  # Si GPU NVIDIA disponible
```

## Architecture de l'Application

### Frontend (Gradio)
- Interface réactive avec streaming des réponses
- Support du chat multimodal (texte + images)
- Gestion du contexte conversationnel
- Système de prompts personnalisables

### Backend (Ollama)
- Serveur d'inférence local
- API REST pour la communication
- Streaming des tokens générés
- Gestion de la mémoire et du contexte

## Pourquoi Ollama ?

### Avantages Clés d'Ollama

1. **Local-First & Open Source**
   - Exécution 100% locale des modèles sans dépendance cloud
   - Pas de coûts d'API ou de limites de requêtes
   - Protection totale des données sensibles
   - [+30k stars sur GitHub](https://github.com/ollama/ollama)

2. **Performance & Optimisation**
   - Optimisé en Golang pour des performances natives
   - Support CUDA/Metal pour accélération GPU
   - Quantification des modèles (4-bit, 8-bit) pour réduire l'empreinte mémoire
   - Streaming des réponses token par token

3. **Modèles Supportés**
   | Modèle | Taille | RAM Min | Description |
   |--------|---------|---------|-------------|
   | Llama 2 | 7B-70B | 8GB-64GB | Modèle Meta, excellent rapport performance/taille |
   | Mistral | 7B | 8GB | Performances proches de GPT-3.5 |
   | Mixtral | 8x7B | 48GB | Mixture-of-Experts, surpasse GPT-3.5 |
   | CodeLlama | 7B-34B | 8GB-32GB | Spécialisé pour le code |
   | Phi-2 | 2.7B | 4GB | Petit modèle Microsoft très efficace |
   | Neural Chat | 7B | 8GB | Optimisé pour le dialogue |

4. **Comparaison avec les Alternatives**

   **Ollama vs OpenAI API**
   - ✅ Gratuit et illimité vs Coût par token
   - ✅ Confidentialité totale vs Données envoyées au cloud
   - ✅ Personnalisation complète vs Modèles fixes
   - ❌ Nécessite du matériel puissant vs Aucune ressource locale
   - ❌ Performances variables vs Performances garanties

   **Ollama vs Hugging Face**
   - ✅ Installation one-click vs Setup complexe
   - ✅ Gestion automatique des modèles vs Configuration manuelle
   - ✅ API simple et unifiée vs APIs différentes par modèle
   - ❌ Moins de modèles disponibles vs Catalogue exhaustif
   - ❌ Moins d'outils de fine-tuning vs Suite complète d'outils ML

### Cas d'Usage Recommandés

1. **Développement & Test**
   ```bash
   # Test rapide d'un prompt
   ollama run llama2 "Explique ce code : $(cat main.py)"
   
   # Génération de tests unitaires
   ollama run codellama "Génère des tests pour cette fonction..."
   ```

2. **Traitement de Données Sensibles**
   ```bash
   # Analyse de logs confidentiels
   ollama run mistral "Analyse ces logs d'erreur : $(tail error.log)"
   
   # Review de code propriétaire
   ollama run codellama "Review ce code : $(git diff)"
   ```

3. **Applications Production**
   ```python
   # Exemple d'intégration API
   import requests
   
   response = requests.post('http://localhost:11434/api/generate',
       json={
           'model': 'llama2',
           'prompt': 'Analyse cette donnée...',
           'system': 'Tu es un expert en analyse de données',
           'format': 'json'  # Sortie structurée
       },
       stream=True  # Streaming pour UX réactive
   )
   ```

### Optimisations Avancées

1. **Réduction Empreinte Mémoire**
   ```bash
   # Modèle 4-bit quantifié
   ollama pull llama2:4bit
   
   # Vérification utilisation mémoire
   ollama show llama2:4bit
   ```

2. **Configuration GPU**
   ```bash
   # Variables d'environnement
   export CUDA_VISIBLE_DEVICES=0  # GPU spécifique
   export OLLAMA_HOST=0.0.0.0    # Accès réseau
   ```

3. **Prompt Engineering**
   ```json
   {
     "system": "Tu es un expert Python qui code de manière idiomatique",
     "template": "Code Review:\n{{.Input}}\n\nSuggestions d'amélioration:\n",
     "parameters": {
       "temperature": 0.7,
       "top_p": 0.9
     }
   }
   ```

## Fonctionnalités Avancées

1. **Gestion du Contexte**
   ```python
   # Exemple d'utilisation du contexte
   messages = [
       {"role": "user", "content": "Question initiale"},
       {"role": "assistant", "content": "Réponse"},
       {"role": "user", "content": "Question suivante"}
   ]
   ```

2. **Support Multimodal**
   ```python
   # Exemple d'envoi d'image
   with open("image.jpg", "rb") as img:
       base64_img = base64.b64encode(img.read()).decode()
   messages = [
       {
           "role": "user",
           "content": "Analyse cette image",
           "images": [base64_img]
       }
   ]
   ```

3. **Prompts Système**
   - Personnalisation du comportement du modèle
   - Templates prédéfinis pour différents cas d'usage
   - Support du few-shot learning

## Modèle Recommandé : llama2-vision

Pour une expérience optimale avec l'interface Gradio, nous recommandons fortement l'utilisation du modèle `llama2-vision:latest` qui offre des capacités multimodales (texte + image) :

1. **Installation du Modèle**
   ```bash
   # Téléchargement du modèle
   ollama pull llama2-vision:latest
   
   # Vérification de l'installation
   ollama list | grep vision
   ```

2. **Configuration dans l'Interface**
   - Lancez l'application : `python app.py`
   - Dans l'interface Gradio, sélectionnez `llama2-vision` dans le menu déroulant des modèles
   - Le modèle supporte maintenant :
     - Questions sur des images
     - Analyse visuelle détaillée
     - Génération de descriptions
     - Détection d'objets et de texte

3. **Exemples d'Utilisation**
   ```python
   # Via l'API
   import requests
   
   response = requests.post('http://localhost:11434/api/generate',
       json={
           'model': 'llama2-vision',
           'prompt': 'Que vois-tu sur cette image ?',
           'images': ['<base64 de l'image>']
       }
   )
   ```

4. **Capacités du Modèle**
   - 🖼️ Analyse d'images haute résolution
   - 📝 Génération de descriptions détaillées
   - 🔍 Détection d'objets et de texte
   - 💡 Réponses contextuelles basées sur le contenu visuel

5. **Performances**
   - RAM recommandée : 16GB minimum
   - GPU : Recommandé pour de meilleures performances
   - Temps de réponse : 2-3 secondes par requête

## Monitoring et Debug

- Logs Ollama : `/var/log/ollama/ollama.log`
- Métriques d'inférence : Temps de réponse, tokens/sec
- Utilisation mémoire : `nvidia-smi` pour GPU

## Ressources Techniques
- [Architecture Transformer](https://arxiv.org/abs/1706.03762)
- [Documentation API Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Guide Gradio Blocks](https://www.gradio.app/guides/blocks-and-event-listeners)

## Contribution
- Fork le projet
- Crée une branche (`git checkout -b feature/amelioration`)
- Commit tes changements (`git commit -am 'Ajout fonctionnalité'`)
- Push sur la branche (`git push origin feature/amelioration`)
- Crée une Pull Request

## Licence
MIT License - Open source et libre d'utilisation