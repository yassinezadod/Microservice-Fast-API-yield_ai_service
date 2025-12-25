import pytest
import pandas as pd
import os
from model_handler import predict_yield
from sklearn.metrics import r2_score, mean_absolute_error

def test_model_performance_from_csv():
    """
    Vérifie les performances du modèle en utilisant le fichier CSV local.
    Utile pour valider l'IA en mode 'Secours' (Fallback).
    """
    # 1. Chargement du fichier CSV
    csv_path = os.path.join("assets", "Data.csv")
    
    if not os.path.exists(csv_path):
        pytest.fail(f"Le fichier {csv_path} est introuvable pour le test.")


    df_test = pd.read_csv(csv_path).sample(frac=0.2, random_state=47)
    
    print(f"\n📊 Test de performance sur {len(df_test)} lignes issues du CSV...")

    # 2. Préparation des listes pour les scores
    y_true = df_test['Rendement (t/ha)'].tolist()
    y_pred = []

    # 3. Simulation de prédiction séquentielle
    # On simule que chaque ligne est une nouvelle donnée arrivant de l'utilisateur
    for _, row in df_test.iterrows():
        input_data = row.to_dict()
        
        # On s'assure que la variété est bien traitée
        pred = predict_yield(input_data)
        y_pred.append(pred)

    # 4. Calcul des métriques
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)

    print("\n" + "="*40)
    print(f"📈 RESULTATS METRIQUES (MODE CSV)")
    print("="*40)
    print(f"⭐ R2 Score : {r2:.4f}")
    print(f"📉 MAE      : {mae:.4f} t/ha")
    print("="*40)

    # 5. Assertions de qualité
    # On accepte un R2 légèrement plus bas sur un échantillon aléatoire, 
    # mais il doit rester performant (> 0.75)
    assert r2 > 0.75, f"Alerte : La précision R2 a chuté à {r2:.4f}"
    assert mae < 1.0, f"Alerte : L'erreur MAE est trop élevée : {mae:.4f}"