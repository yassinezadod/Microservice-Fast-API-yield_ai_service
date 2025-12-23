import pytest
import joblib
import pandas as pd
import numpy as np
import os
import sys

# Patch pour la classe custom (indispensable)
from application.ml.feature_engineering import FeatureEngineering
sys.modules['__main__'].FeatureEngineering = FeatureEngineering

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "application", "ml", "pipeline_champion.pkl")

# Liste des 20 colonnes brutes attendues par ton transformer
FEATURE_COLUMNS = [
    'Semaine', 'Jour apres plantation', 'Vitesse de maturation', 'variete',
    'ETo (mm)', 'Temperature (Min) (C)', 'Temperature (Moy) (C)',
    'Temperature (Max) (C)', 'Humidite relative (Min) (%)',
    'Humidite relative (Moy) (%)', 'Humidite relative (Max) (%)',
    'Rayonnement global (j/cm2)', 'VPD (Min) (Kpa)', 'VPD (Kpa)',
    'VPD (Max) (Kpa)', 'Degre jour (C)', 'Cumul degres jour  (C)',
    'Amplitude thermique (C)', 'Indice de chaleur (C)', 'Point de rosee (C)'
]

def test_pipeline_inference():
    """ Teste si le pipeline transforme bien les 20 colonnes en prédiction """
    
    # 1. Charger le pipeline
    if not os.path.exists(MODEL_PATH):
        pytest.fail(f"Modèle introuvable : {MODEL_PATH}")
    
    pipeline = joblib.load(MODEL_PATH)
    
    # 2. Créer une donnée fictive (1 ligne, 20 colonnes)
    # On utilise des valeurs moyennes réalistes
    sample_data = {
        'Semaine': 12,
        'Jour apres plantation': 45,
        'Vitesse de maturation': 1.2,
        'variete': "208",
        'ETo (mm)': 3.5,
        'Temperature (Min) (C)': 15.0,
        'Temperature (Moy) (C)': 22.0,
        'Temperature (Max) (C)': 30.0,
        'Humidite relative (Min) (%)': 40.0,
        'Humidite relative (Moy) (%)': 65.0,
        'Humidite relative (Max) (%)': 85.0,
        'Rayonnement global (j/cm2)': 1800.0,
        'VPD (Min) (Kpa)': 0.5,
        'VPD (Kpa)': 1.2,
        'VPD (Max) (Kpa)': 2.5,
        'Degre jour (C)': 12.0,
        'Cumul degres jour  (C)': 450.0,
        'Amplitude thermique (C)': 15.0,
        'Indice de chaleur (C)': 24.0,
        'Point de rosee (C)': 12.0
    }
    
    df_test = pd.DataFrame([sample_data], columns=FEATURE_COLUMNS)

    # 3. Exécuter la prédiction
    # Le pipeline va appeler FeatureEngineering._create_all_features en interne
    try:
        prediction = pipeline.predict(df_test)
        
        print(f"\n✅ Prédiction réussie : {prediction[0]:.4f} t/ha")
        
        # Assertions
        assert isinstance(prediction[0], (float, np.float64))
        assert prediction[0] > 0, "Le rendement ne peut pas être négatif"
        
    except Exception as e:
        pytest.fail(f"Le pipeline a échoué lors de la transformation : {e}")

def test_feature_engineering_logic():
    """ Teste spécifiquement si la classe crée bien les colonnes calculées """
    fe = FeatureEngineering()
    
    # Simuler un petit DF pour le fit (nécessaire pour duree_par_variete)
    df_fit = pd.DataFrame({
        'variete': [208],
        'Jour apres plantation': [100],
        'Semaine': [1], 'Vitesse de maturation': [1], 'ETo (mm)': [1],
        'Temperature (Min) (C)': [1], 'Temperature (Moy) (C)': [25], 'Temperature (Max) (C)': [30],
        'Humidite relative (Min) (%)': [60], 'Humidite relative (Moy) (%)': [70], 'Humidite relative (Max) (%)': [80],
        'Rayonnement global (j/cm2)': [1000], 'Degre jour (C)': [10], 'Cumul degres jour  (C)': [100],
        'Amplitude thermique (C)': [5], 'Indice de chaleur (C)': [25], 'Point de rosee (C)': [15]
    })
    
    fe.fit(df_fit)
    transformed = fe.transform(df_fit)
    
    # Vérifier que les colonnes complexes sont là
    assert 'progres_sin' in transformed.columns
    assert 'phase_croissance_encoded' in transformed.columns
    print(f"✅ Feature Engineering validé : {transformed.shape[1]} colonnes générées.")

if __name__ == "__main__":
    pytest.main([__file__, "-s"])