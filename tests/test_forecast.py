import pytest
from model_handler import predict_yield
from database import get_history_collection

def test_prediction_from_mongodb():
    print("\n--- TEST DE PRÉCISION ET CALCUL D'ERREUR (MONGODB) ---")
    
    collection = get_history_collection()
    
    # 1. On récupère les données (Semaine est un nombre, variete est un nombre)
    query = {
        "Semaine": {"$in": [2, 3, 4, 5]},
        "variete": 2010
    }
    
    # .sort("Semaine", 1) est crucial pour l'ordre chronologique
    records = list(collection.find(query).sort("Semaine", 1))

    if not records:
        pytest.fail("❌ Aucune donnée trouvée. Vérifie si 'Semaine' et 'variete' sont bien des nombres dans ta base.")

    print(f"✅ {len(records)} semaines trouvées. Calcul de la précision...\n")
    
    # Rendement de départ (Semaine 1)
    last_yield = 3.5 
    somme_erreurs = 0
    compteur = 0

    for doc in records:
        sem = doc["Semaine"]
        payload = dict(doc)
        if "_id" in payload: del payload["_id"]
        
        # On injecte le rendement précédent
        payload["Rendement (t/ha)"] = last_yield
        
        # Prédiction IA
        prediction = predict_yield(payload)
        
        # Valeur réelle
        reel = doc.get("Rendement (t/ha)")
        
        if reel is not None:
            erreur = abs(prediction - reel)
            somme_erreurs += erreur
            compteur += 1
            status = "✅" if erreur < 0.5 else "⚠️"
            print(f"Semaine {sem} | IA: {prediction:.3f} | Réel: {reel:.1f} | Erreur: {round(erreur, 3)} t/ha {status}")
        
        # Mise à jour pour la semaine suivante
        last_yield = prediction

    # 2. Calcul du score final (MAE)
    if compteur > 0:
        mae = somme_erreurs / compteur
        print(f"\n--- SCORE FINAL ---")
        print(f"Erreur moyenne (MAE) : {round(mae, 3)} t/ha")
        print(f"Nombre de semaines testées : {compteur}")

    print("--- Fin du test ---")