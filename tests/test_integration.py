# from fastapi.testclient import TestClient
# from main import app
# import pytest

# client = TestClient(app)

# def test_health_check():
#     """Vérifie que l'API est en ligne"""
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json()["status"] == "online"

# def test_api_prediction_flow():
#     """Vérifie le cycle complet : Requête JSON -> Prédiction -> Réponse"""
#     payload = {
#         "Semaine": 15,
#         "Jour_apres_plantation": 60,
#         "Vitesse_de_maturation": 0.8,
#         "variete": "2050",
#         "ETo_mm": 4.2,
#         "Temperature_Min_C": 18.2,
#         "Temperature_Moy_C": 24.5,
#         "Temperature_Max_C": 32.0,
#         "Humidite_relative_Min_pct": 35.0,
#         "Humidite_relative_Moy_pct": 55.0,
#         "Humidite_relative_Max_pct": 75.0,
#         "Rayonnement_global_j_cm2": 2100.0,
#         "VPD_Min_Kpa": 0.6,
#         "VPD_Kpa": 1.4,
#         "VPD_Max_Kpa": 2.8,
#         "Degre_jour_C": 14.0,
#         "Cumul_degres_jour_C": 600.0,
#         "Amplitude_thermique_C": 13.8,
#         "Indice_de_chaleur_C": 26.0,
#         "Point_de_rosee_C": 14.0
#     }
#     response = client.post("/predict", json=payload)
    
#     assert response.status_code == 200
#     data = response.json()
#     assert "prediction_yield" in data
#     assert data["status"] == "success"

# def test_prediction_invalid_data():
#     """Vérifie que l'API rejette les données incomplètes"""
#     response = client.post("/predict", json={"variete": "inconnue"})
#     assert response.status_code == 400