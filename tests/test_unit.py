import pytest
import pandas as pd
import numpy as np
from model_handler import create_features, get_feature_list, predict_yield

def test_feature_creation_logic():
    """Vérifie que le Feature Engineering génère bien les 33 colonnes"""
    data = {
        'Semaine': [10],
        'Jour apres plantation': [50],
        'Vitesse de maturation': [1.0],
        'variete': ['2050'],
        'ETo (mm)': [4.0],
        'Temperature (Min) (C)': [15.0],
        'Temperature (Moy) (C)': [22.0],
        'Temperature (Max) (C)': [30.0],
        'Humidite relative (Min) (%)': [40.0],
        'Humidite relative (Moy) (%)': [60.0],
        'Humidite relative (Max) (%)': [80.0],
        'Rayonnement global (j/cm2)': [2000.0],
        'Degre jour (C)': [10.0],
        'Cumul degres jour  (C)': [500.0],
        'Amplitude thermique (C)': [15.0],
        'Indice de chaleur (C)': [25.0],
        'Point de rosee (C)': [12.0]
    }
    df = pd.DataFrame(data)
    df_feat = create_features(df, is_init=False)
    
    # Vérification des colonnes créées
    assert 'progres' in df_feat.columns
    assert 'phase_croissance' in df_feat.columns
    assert df_feat['progres'].iloc[0] <= 1.0
    assert isinstance(df_feat['variete'].iloc[0], str)

def test_predict_yield_output_type():
    """Vérifie que la fonction de prédiction retourne un float arrondi"""
    sample = {
        'Semaine': 12, 'Jour apres plantation': 45, 'Vitesse de maturation': 1.2,
        'variete': '2050', 'ETo (mm)': 3.5, 'Temperature (Min) (C)': 15.0,
        'Temperature (Moy) (C)': 22.0, 'Temperature (Max) (C)': 30.0,
        'Humidite relative (Min) (%)': 40.0, 'Humidite relative (Moy) (%)': 65.0,
        'Humidite relative (Max) (%)': 85.0, 'Rayonnement global (j/cm2)': 1800.0,
        'Degre jour (C)': 12.0, 'Cumul degres jour  (C)': 450.0,
        'Amplitude thermique (C)': 15.0, 'Indice de chaleur (C)': 24.0,
        'Point de rosee (C)': 12.0
    }
    prediction = predict_yield(sample)
    assert isinstance(prediction, float)