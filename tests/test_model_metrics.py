import pytest
import pandas as pd
from model_handler import predict_yield, get_feature_list
from database import get_history_collection
from sklearn.metrics import r2_score, mean_absolute_error

def test_model_performance_from_mongodb():
    """Vérifie que le modèle maintient ses performances (R2 > 0.80) avec MongoDB"""
    
    # 1. Extraction des données de test depuis MongoDB
    history_col = get_history_collection()
    cursor = history_col.find({"provenance": "csv_import"}, {"_id": 0})
    df_test = pd.DataFrame(list(cursor))
    
    if df_test.empty:
        pytest.fail("La base MongoDB est vide, impossible de tester les performances.")

    print(f"\n📊 Test de performance sur {len(df_test)} lignes issues de MongoDB...")

    # 2. Préparation des listes pour comparer
    y_true = df_test['Rendement (t/ha)'].tolist()
    y_pred = []

    # 3. Calcul des prédictions ligne par ligne
    for _, row in df_test.iterrows():
        # On passe la ligne entière à la fonction de prédiction
        pred = predict_yield(row.to_dict())
        y_pred.append(pred)

    # 4. Calcul des scores
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)

    print(f"✅ Résultat du Test - R2 Score: {r2:.4f}")
    print(f"✅ Résultat du Test - MAE: {mae:.4f}")

    # 5. Validation (Le test échoue si le score chute trop)
    assert r2 > 0.80, f"Le score R2 est trop bas: {r2:.4f}"