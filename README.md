# 🌾 Smart Agri Yield Service (Microservice IA)

Ce microservice Python basé sur **FastAPI** est le moteur d'intelligence artificielle du projet Yield AI. Il gère les prédictions de rendement, l'analyse de précision et la synchronisation automatisée des données historiques.

---

## 🚀 Architecture du Pipeline de Données

Le service est conçu comme un système en boucle fermée (Closed-Loop) :

1. **Traitement** : FastAPI reçoit les données climatiques et agro de Laravel.
2. **IA** : Le modèle `LightGBM` (champion_model.pkl) génère des prévisions sur 4 semaines.
3. **Validation** : Le service compare les prévisions aux rendements réels saisis par l'utilisateur.
4. **Apprentissage** : Les données validées sont automatiquement synchronisées dans **MongoDB** pour constituer un dataset de ré-entraînement.

---

## 🛠️ Installation et Configuration

### 1. Prérequis

- Python 3.13+
- MongoDB (Local ou Atlas)
- Environnement virtuel chargé

### 2. Configuration (.env)

Créez un fichier `.env` à la racine (déjà présent dans votre dossier local) :

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=Your database name
MONGO_COLLECTION_HISTORY=history
LARAVEL_SYNC_URL=http://localhost:8001/api/yield/sync-data
LARAVEL_SYNC_KEY=votre_cle_secrete_hexadecimale
```

---

### 3. Installation

```bash
# Avec Poetry (recommandé)
poetry install

# Avec Pip
pip install -r requirements.txt
```

### 4. Démarrage du Service

Pour lancer le microservice en mode développement avec rechargement automatique :

```bash
poetry run start
```

- **API URL** : http://127.0.0.1:8000
- **Documentation Swagger** : http://127.0.0.1:8000/docs

### 5. Liste des Endpoints API

| Catégorie  | Méthode | Endpoint             | Description                                        |
| ---------- | ------- | -------------------- | -------------------------------------------------- |
| Prédiction | POST    | /predict             | Prédit le rendement sur 4 semaines (33 variables). |
| Analyse    | POST    | /api/compare         | Calcule MAE, RMSE et Fiabilité (%).                |
| Système    | POST    | /api/sync-history    | Déclenche la synchro automatique vers MongoDB.     |
| Données    | GET     | /api/predict/history | Récupère l'historique stocké dans MongoDB.         |
| Monitoring | GET     | /metrics             | Affiche la précision actuelle du modèle.           |

### 6. Structure des Fichiers

- **main.py** : Entrée de l'application et définition des routes FastAPI.
- **model_handler.py** : Logique de chargement du modèle et calcul des prédictions.
- **sync_service.py** : Moteur de synchronisation asynchrone Laravel ↔ MongoDB.
- **database.py** : Gestion de la connexion à la base MongoDB.
- **champion_model.pkl** : Modèle LightGBM entraîné.
- **tests/** : Dossier contenant les tests unitaires (pytest).

### 7. Cycle d'Apprentissage Continu (Automatique)

Ce microservice utilise les BackgroundTasks de FastAPI. Lorsqu'une comparaison est effectuée dans Laravel, un signal est envoyé à `/api/sync-history`. Le service Python va alors :

- Aspirer les données de production depuis Laravel.
- Formater les données (33 features agro-climatiques).
- Vérifier les doublons.
- Enregistrer la "vérité terrain" dans MongoDB.
