from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Importation de tes fonctions logiques depuis model_handler.py
from model_handler import predict_next_4_weeks, get_performance_metrics

app = FastAPI(
    title="Smart-Agri AI Service",
    description="Microservice de prédiction de rendement avec LightGBM/XGBoost",
    version="1.0.0"
)

# --- Schémas de données (Pydantic) ---

class PredictionRequest(BaseModel):
    semaine: int
    rendement_initial: float
    variete: int

class PredictionResponse(BaseModel):
    semaine: int
    valeur_predite: float

class MetricsResponse(BaseModel):
    model_name: str
    performance: dict

# --- Routes API ---

@app.get("/")
def home():
    return {
        "message": "AI Service is Online",
        "docs": "/docs"
    }

@app.post("/predict", response_model=dict)
async def run_prediction(request: PredictionRequest):
    """
    Calcule les prédictions S1, S2, S3, S4 basées sur l'entrée utilisateur
    """
    try:
        results = predict_next_4_weeks(
            request.semaine, 
            request.rendement_initial, 
            request.variete
        )
        
        if not results:
            raise HTTPException(status_code=404, detail="Modèle non chargé ou données insuffisantes")
            
        return {
            "status": "success",
            "input": request,
            "predictions": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

@app.get("/metrics", response_model=MetricsResponse)
async def get_model_stats():
    """
    Retourne les métriques R2 et MAE calculées sur la base MongoDB
    """
    stats = get_performance_metrics()
    
    if "error" in stats:
        raise HTTPException(status_code=400, detail=stats["error"])
        
    return {
        "model_name": "Champion Model (from Notebook)",
        "performance": stats
    }

# --- Lancement du serveur ---

if __name__ == "__main__":
    # Le port 8001 est choisi pour ne pas entrer en conflit avec Laravel (8000)
    uvicorn.run(app, host="127.0.0.1", port=8001)