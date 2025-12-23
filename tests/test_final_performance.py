import os
import pandas as pd
import joblib
from sklearn.metrics import r2_score, mean_absolute_error

# 🔹 Importer la classe personnalisée
from application.ml.feature_engineering import FeatureEngineering

MODEL_PATH = "application/ml/pipeline_champion.pkl"
CSV_PATH = "DataClean.csv"

def test_pipeline_performance():
    # 1️⃣ Vérifier que le modèle existe
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Le modèle n'a pas été trouvé : {MODEL_PATH}")
    
    # 🔹 Charger le pipeline après import de FeatureEngineering
    pipeline = joblib.load(MODEL_PATH)

    # 2️⃣ Charger les données
    df_test = pd.read_csv(CSV_PATH, sep=';', dtype={'variete': str})

    # 3️⃣ Vérifier la colonne cible
    if 'Rendement (t/ha)' not in df_test.columns:
        raise ValueError("Colonne cible 'Rendement (t/ha)' introuvable dans le CSV !")

    y_true = df_test['Rendement (t/ha)']
    X_test = df_test.drop(columns=['Rendement (t/ha)'])

    # 4️⃣ Prédiction
    y_pred = pipeline.predict(X_test)

    # 5️⃣ Calcul des métriques
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)

    print("="*50)
    print("📊 PERFORMANCE DU MODELE")
    print("="*50)
    print(f"✅ Coefficient R² : {r2:.4f}")
    print(f"✅ Erreur MAE      : {mae:.4f} t/ha")
    print("-"*50)

    # Assertion facultative
    assert r2 > 0.5, f"R² trop faible : {r2:.4f}"
