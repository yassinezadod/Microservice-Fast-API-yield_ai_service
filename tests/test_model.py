import pytest
import joblib
import pandas as pd
import numpy as np

def test_model_loading():
    """Vérifie que le fichier pkl est valide"""
    model = joblib.load('champion_model.pkl')
    assert model is not None
    # Vérifie que c'est bien un modèle qui a une méthode predict
    assert hasattr(model, 'predict')

def test_model_prediction_shape():
    """Vérifie que le modèle accepte les 33 colonnes et répond"""
    model = joblib.load('champion_model.pkl')
    
    # Création d'une ligne de test avec 33 colonnes (zéros)
    dummy_input = pd.DataFrame(np.zeros((1, 33)))
    
    prediction = model.predict(dummy_input)
    
    assert len(prediction) == 1
    assert isinstance(prediction[0], (float, np.float64, np.float32))