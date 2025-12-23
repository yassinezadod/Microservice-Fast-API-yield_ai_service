import pytest
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import os
import sys

# On s'assure que le dossier racine est dans le path pour importer model_handler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_handler import predict_yield, DATA_PATH

def test_model_performance_r2():
    """
    Test de validation des performances avec pytest :
    Vérifie que le flux complet du model_handler maintient le score R2 champion.
    """
    # 1. Vérifier la présence du fichier de données
    assert os.path.exists(DATA_PATH), f"Le fichier {DATA_PATH} est requis pour le test."

    # 2. Charger les données pour le test (on prend un échantillon aléatoire)
    df_raw = pd.read_csv(DATA_PATH)
    test_samples = df_raw.sample(frac=0.2, random_state=42)
    
    y_true = test_samples['Rendement (t/ha)'].values
    y_pred = []

    # 3. Exécuter les prédictions via le model_handler
    # Cela teste l'initialisation du scaler et des encoders
    for _, row in test_samples.iterrows():
        # On prépare le dictionnaire comme le fera l'API
        input_data = row.drop('Rendement (t/ha)').to_dict()
        
        try:
            prediction = predict_yield(input_data)
            y_pred.append(prediction)
        except Exception as e:
            pytest.fail(f"Erreur lors de la prédiction pour la ligne {row.name}: {e}")

    # 4. Calcul des métriques
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    
    # Affichage des résultats dans la console (visible avec -s)
    print(f"\n" + "="*40)
    print(f"📊 RÉSULTATS DU TEST PYTEST")
    print(f"✅ R2 Score : {r2:.4f}")
    print(f"✅ MAE      : {mae:.4f} t/ha")
    print("="*40)

    # 5. Assertions
    # On autorise une petite marge par rapport au 0.7337 (ex: 0.70)
    assert r2 > 0.65, f"La précision R2 est tombée à {r2:.4f} !"
    assert mae < 1.0, f"L'erreur MAE est trop élevée : {mae:.4f}"