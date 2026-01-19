# 1. Image de base légère avec Python 3.13
FROM python:3.13-slim

# --- AJOUT : Empêcher Python de mettre les logs en mémoire tampon ---
ENV PYTHONUNBUFFERED=1

# 2. Définition du répertoire de travail dans le conteneur
WORKDIR /app

# 3. Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copie du fichier des dépendances
COPY requirements.txt .

# 5. Installation des librairies Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copie de tout le projet dans le conteneur
# (Copie main.py, model_handler.py, champion_model.pkl, .env, assets/, etc.)
COPY . .

# 7. Exposition du port 8000
EXPOSE 8000

# 8. Commande pour démarrer l'application
CMD ["python", "main.py"]