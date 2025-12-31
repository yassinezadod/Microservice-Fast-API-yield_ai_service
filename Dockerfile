# 1. Image de base légère avec Python 3.13
FROM python:3.13-slim

# 2. Définition du répertoire de travail dans le conteneur
WORKDIR /app

# 3. Installation des dépendances système nécessaires (pour compiler certains paquets si besoin)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copie du fichier des dépendances
COPY requirements.txt .

# 5. Installation des librairies Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copie de tout le projet dans le conteneur
# Cela inclut main.py, model_handler.py, champion_model.pkl et le dossier assets/
COPY . .

# 7. Exposition du port 8000 (port par défaut de ton API)
EXPOSE 8000

# 8. Commande pour démarrer l'application
# On utilise directement python main.py car tu as configuré uvicorn à l'intérieur
CMD ["python", "main.py"]