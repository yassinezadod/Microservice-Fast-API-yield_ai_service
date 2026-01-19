import pytest
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error
from model_handler import predict_yield
from database import get_history_collection

def test_global_performance_report():
    """
    Analyse automatique de TOUTES les variétés présentes dans la base de données.
    Calcule MAE et R2 pour chaque groupe.
    """
    print("\n" + "="*60)
    print("🚀 RAPPORT DE PERFORMANCE GLOBAL (TOUTES VARIÉTÉS)")
    print("="*60)
    
    collection = get_history_collection()
    
    # 1. Récupérer la liste de toutes les variétés uniques
    varietes = collection.distinct("variete")
    
    if not varietes:
        pytest.fail("❌ Aucune donnée trouvée dans la collection.")

    global_stats = []

    for var in varietes:
        print(f"\nAnalyse de la Variété : {var}")
        print("-" * 30)
        
        # Récupérer les données triées pour cette variété
        records = list(collection.find({"variete": var}).sort("Semaine", 1))
        
        if len(records) < 2:
            print(f"⚠️ Pas assez de données pour {var} (min. 2 semaines requises)")
            continue

        y_true = []
        y_pred = []
        
        # Initialisation du rendement précédent (on prend le premier réel)
        last_yield = records[0].get("Rendement (t/ha)", 0)

        for doc in records:
            payload = dict(doc)
            if "_id" in payload: del payload["_id"]
            
            # Injection de l'état précédent
            payload["Rendement (t/ha)"] = last_yield
            
            # Prédiction
            prediction = predict_yield(payload)
            reel = doc.get("Rendement (t/ha)")
            
            if reel is not None:
                y_true.append(reel)
                y_pred.append(prediction)
                last_yield = reel  # On suit la réalité pour le test de précision
                
        # Calcul des scores pour cette variété
        if len(y_true) > 1:
            mae = mean_absolute_error(y_true, y_pred)
            try:
                r2 = r2_score(y_true, y_pred)
            except:
                r2 = 0 # Cas où le rendement est constant
            
            status = "✅" if r2 > 0.6 else "⚠️"
            print(f"   📊 MAE : {mae:.3f} t/ha")
            print(f"   📈 R²  : {r2:.3f} {status}")
            print(f"   🔢 Points : {len(y_true)}")
            
            global_stats.append({
                "variete": var,
                "mae": mae,
                "r2": r2,
                "points": len(y_true)
            })

    # --- RÉSUMÉ FINAL ---
    print("\n" + "="*60)
    print("      CLASSEMENT FINAL DES VARIÉTÉS PAR FIABILITÉ")
    print("="*60)
    # Trier par R2 décroissant
    global_stats.sort(key=lambda x: x['r2'], reverse=True)
    
    for stat in global_stats:
        print(f"Variété {stat['variete']} | R²: {stat['r2']:.3f} | MAE: {stat['mae']:.3f}")

    print("="*60)