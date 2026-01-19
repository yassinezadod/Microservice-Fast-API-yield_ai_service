from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Récupération via les variables d'environnement
# On ne met plus "smart_agri_db" ici, on utilise uniquement os.getenv
uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_DB_NAME")
collection_name = os.getenv("MONGO_COLLECTION_HISTORY")

# Initialisation de la connexion
client = MongoClient(uri)
db = client[db_name]

def get_history_collection():
    """Retourne la collection définie dans le fichier .env"""
    return db[collection_name]