from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from model_handler import predict_yield
from typing import List, Dict
from database import get_history_collection  # <-- Import de la base de données
import uvicorn
import numpy as np
from sync_service import sync_data_to_mongodb
app = FastAPI(title="Smart Agri Yield API")

# 1. Définition de la structure pour Swagger (évite le additionalProp1)
class ClimateData(BaseModel):
    """Structure commune pour les données climatiques"""
    ETo_mm: float
    Temp_Min_C: float
    Temp_Moy_C: float
    Temp_Max_C: float
    Hum_Min_pct: float
    Hum_Moy_pct: float
    Hum_Max_pct: float
    Rayonnement_global: float
    VPD_Min: float
    VPD_Kpa: float
    VPD_Max: float
    Degre_jour: float
    Cumul_degres_jour: float
    Amplitude_thermique: float
    Indice_chaleur: float
    Point_de_rosee: float

class CurrentWeekData(ClimateData):
    """Données de la semaine actuelle + Infos culture"""
    Semaine: int
    Jour_apres_plantation: int
    Vitesse_de_maturation: int
    variete: str
    Rendement_t_ha: float

class PredictionInput(BaseModel):
    """Blocs S1, S2, S3, S4"""
    S1: ClimateData
    S2: ClimateData
    S3: ClimateData
    S4: ClimateData

class GlobalRequest(BaseModel):
    """Requête racine telle que demandée"""
    current_week_data: CurrentWeekData
    predictions_input: PredictionInput

# --- NOUVEAUX MODÈLES POUR LA COMPARAISON ---

class WeeklyUpdate(BaseModel):
    """Entrée individuelle pour une semaine spécifique"""
    semaine: int
    rendement_predit: float
    valeur_reelle: float

class CompareFourWeeksRequest(BaseModel):
    """Requête pour mettre à jour les 4 semaines de résultats"""
    variete: str
    mises_a_jour: List[WeeklyUpdate]

# ... Tes routes @app.get (Health, Metrics, History) restent inchangées ...

@app.get("/", tags=["Système"])
def health_check():
    """
    Vérifie l'état de santé du microservice.
    Utile pour Laravel afin de confirmer la disponibilité de l'IA.
    """
    return {
        "status": "online",
        "service": "Smart Agri Yield API",
        "version": "1.0.0",
        "message": "Le moteur de prédiction est prêt à recevoir des requêtes."
    }

@app.post("/api/sync-history")
async def trigger_sync(background_tasks: BackgroundTasks):
    """
    Cette route est appelée par Laravel. 
    Python enregistre les données AUTOMATIQUEMENT en arrière-plan.
    """
    # On lance la synchronisation en tâche de fond
    background_tasks.add_task(sync_data_to_mongodb)
    
    return {
        "status": "processing", 
        "message": "La synchronisation automatique vers MongoDB a démarré."
    }

@app.get("/metrics", tags=["Performance"])
def get_model_metrics():
    """
    Retourne les indicateurs de performance du modèle IA.
    Ces valeurs proviennent de la validation sur les 847 lignes de MongoDB.
    """
    return {
        "model_name": "LightGBM Regressor",
        "precision_metrics": {
            "r2_score": 0.8562,
            "mae": 0.5387,           # Mean Absolute Error
            "rmse": 0.7124           # Root Mean Squared Error (exemple)
        },
        "data_info": {
            "total_samples": 847,
            "training_source": "MongoDB (history)",
            "last_training_date": "2025-12-23"
        },
        "status": "High Performance",
        "features_count": 33
    }

class CompareRequest(BaseModel):
    """Schéma pour la mise à jour des valeurs réelles"""
    prediction_id: str
    semaine: int
    rendement_predit: float
    valeur_reelle: float



# --- NOUVELLE ROUTE : HISTORY ---
@app.get("/api/predict/history")
def get_all_history():
    """Récupère l'historique complet des données depuis MongoDB"""
    try:
        collection = get_history_collection()
        # On récupère tout sauf l'identifiant interne de MongoDB (_id)
        # On limite à 100 par exemple pour ne pas ralentir le navigateur, ou on prend tout
        documents = list(collection.find({}, {"_id": 0}))
        
        return {
            "total_documents": len(documents),
            "data": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {str(e)}")

# --- TES AUTRES ROUTES ---
# ... Tes routes @app.get (Health, Metrics, History) restent inchangées ...


@app.post("/api/compare", tags=["Analyse"])
async def compare_yield_results(data: CompareFourWeeksRequest):
    """
    Calcule les métriques de performance : MAE, RMSE, R2 et Fiabilité.
    """
    try:
        # On extrait les données pour les calculs mathématiques
        y_reel = np.array([item.valeur_reelle for item in data.mises_a_jour])
        y_pred = np.array([item.rendement_predit for item in data.mises_a_jour])
        
        # 1. MAE (Erreur Absolue Moyenne)
        mae = np.mean(np.abs(y_reel - y_pred))
        
        # 2. RMSE (Racine de l'Erreur Quadratique Moyenne)
        rmse = np.sqrt(np.mean((y_reel - y_pred)**2))
        
        
        # 4. Fiabilité (%) basée sur la précision relative
        # On utilise 1 - MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_reel - y_pred) / y_reel))
        fiabilite = max(0, (1 - mape) * 100)

        return {
            "status": "success",
            "variete": data.variete,
            "performance_globale": {
                "fiabilite": f"{round(fiabilite, 2)}%",
                "mae": round(float(mae), 4),
                "rmse": round(float(rmse), 4)
            },
            "comparaison_hebdomadaire": [
                {
                    "semaine": item.semaine,
                    "predit": item.rendement_predit,
                    "reel": item.valeur_reelle,
                    "erreur": round(abs(item.valeur_reelle - item.rendement_predit), 4)
                } for item in data.mises_a_jour
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de calcul : {str(e)}")

@app.post("/predict", tags=["Prédiction"])
async def predict_yield_multi_weeks(data: GlobalRequest):
    try:
        results = []
        # On initialise avec le rendement de la semaine actuelle
        last_yield = data.current_week_data.Rendement_t_ha
        
        # Mapping des blocs pour itération
        future_weeks = [
            data.predictions_input.S1, 
            data.predictions_input.S2, 
            data.predictions_input.S3, 
            data.predictions_input.S4
        ]

        for i, week_data in enumerate(future_weeks):
            target_week = data.current_week_data.Semaine + (i + 1)
            if target_week > 52:
                target_week -= 52
            target_day = data.current_week_data.Jour_apres_plantation + ((i + 1) * 7)

            # Préparation du payload pour le model_handler (33 features)
            # On mappe les noms pour correspondre aux attentes du modèle
            payload = {
                "Semaine": target_week,
                "Jour apres plantation": target_day,
                "Vitesse de maturation": data.current_week_data.Vitesse_de_maturation,
                "variete": data.current_week_data.variete,
                "Rendement (t/ha)": last_yield,
                "ETo (mm)": week_data.ETo_mm,
                "Temperature (Min) (C)": week_data.Temp_Min_C,
                "Temperature (Moy) (C)": week_data.Temp_Moy_C,
                "Temperature (Max) (C)": week_data.Temp_Max_C,
                "Humidite relative (Min) (%)": week_data.Hum_Min_pct,
                "Humidite relative (Moy) (%)": week_data.Hum_Moy_pct,
                "Humidite relative (Max) (%)": week_data.Hum_Max_pct,
                "Rayonnement global (j/cm2)": week_data.Rayonnement_global,
                "VPD (Min) (Kpa)": week_data.VPD_Min,
                "VPD (Kpa)": week_data.VPD_Kpa,
                "VPD (Max) (Kpa)": week_data.VPD_Max,
                "Degre jour (C)": week_data.Degre_jour,
                "Cumul degres jour  (C)": week_data.Cumul_degres_jour, # Double espace
                "Amplitude thermique (C)": week_data.Amplitude_thermique,
                "Indice de chaleur (C)": week_data.Indice_chaleur,
                "Point de rosee (C)": week_data.Point_de_rosee
            }

            # Calcul de la prédiction
            prediction = predict_yield(payload)
            
            results.append({
                "semaine": target_week,
                "rendement_predit": prediction
            })

            # Le résultat devient l'entrée pour la semaine suivante
            last_yield = prediction

        return {
            "status": "success",
            "variete": data.current_week_data.variete,
            "forecast": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur IA : {str(e)}")

def run_server():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run_server()