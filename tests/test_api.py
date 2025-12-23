from fastapi.testclient import TestClient
from main import app # On importe ton application FastAPI

client = TestClient(app)

def test_read_main():
    """Vérifie que le service est en ligne"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Service is Online", "docs": "/docs"}

def test_predict_endpoint_error():
    """Vérifie que l'API renvoie une erreur si les données sont incomplètes"""
    payload = {
        "semaine": 12,
        "rendement_initial": 1.5,
        "variete": 1
    }
    response = client.post("/predict", json=payload)
    
    # On s'attend à une erreur 500 car il manque les 33 colonnes 
    # tant que model_handler n'est pas corrigé
    assert response.status_code == 500 
    assert "features" in response.json()["detail"]