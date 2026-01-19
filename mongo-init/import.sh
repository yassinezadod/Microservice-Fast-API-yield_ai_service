#!/bin/bash
# Script d'importation automatique au démarrage du conteneur MongoDB

echo "----------------------------------------------------------------"
echo "🚀 [INIT DB] Début de l'importation du fichier assets/Data.csv..."
echo "----------------------------------------------------------------"

# Commande native mongoimport
# --db : Nom de la base de données cible (yield_ai_db)
# --collection : Nom de la collection (history)
# --type csv : Format source
# --file : Chemin du fichier MONTÉ dans le conteneur via docker-compose
# --headerline : Utilise la 1ère ligne du CSV pour les noms des colonnes
mongoimport --db smart_agri_db \
            --collection history \
            --type csv \
            --file /docker-entrypoint-initdb.d/Data.csv \
            --headerline

# Vérification du code de sortie
if [ $? -eq 0 ]; then
    echo "----------------------------------------------------------------"
    echo "✅ [INIT DB] Importation réussie dans MongoDB !"
    echo "----------------------------------------------------------------"
else
    echo "----------------------------------------------------------------"
    echo "❌ [INIT DB] Échec de l'importation. Vérifiez le fichier CSV."
    echo "----------------------------------------------------------------"
fi