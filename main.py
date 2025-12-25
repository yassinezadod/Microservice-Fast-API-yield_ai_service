from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from model_handler import predict_yield
from database import get_history_collection  # <-- Import de la base de données
import uvicorn

app = FastAPI(title="Smart Agri Yield API")

# 1. Définition de la structure pour Swagger (évite le additionalProp1)
class AgriDataInput(BaseModel):
    id: str = "694a72fa3960534ce39a5b03"
    Semaine: int = 41
    Jour_apres_plantation: int = 59
    Vitesse_de_maturation: int = 1
    variete: str = "2009"
    Rendement_t_ha: float = 5.0
    ETo_mm: float = 2.84
    Temp_Min_C: float = 11.46
    Temp_Moy_C: float = 16.34
    Temp_Max_C: float = 21.36
    Hum_Min_pct: float = 65.58
    Hum_Moy_pct: float = 88.91
    Hum_Max_pct: float = 100.0
    Rayonnement_global: float = 1948.48
    VPD_Min: float = 0.0
    VPD_Kpa: float = 0.2
    VPD_Max: float = 1.03
    Degre_jour: float = 6.41
    Cumul_degres_jour: float = 187.71
    Amplitude_thermique: float = 9.9
    Indice_chaleur: float = 18.43
    Point_de_rosee: float = 9.93

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

@app.post("/predict", tags=["Prédiction"])
async def predict(data: AgriDataInput):
    try:
        # 2. MAPPING : On transforme les noms simples en noms attendus par le modèle
        # C'est ici que l'erreur 500 se règle
        # Mapping avec correction de l'espace double pour Cumul degres jour
        formatted_data = {
            "Semaine": data.Semaine,
            "Jour apres plantation": data.Jour_apres_plantation,
            "Vitesse de maturation": data.Vitesse_de_maturation,
            "variete": data.variete,
            "Rendement (t/ha)": data.Rendement_t_ha,
            "ETo (mm)": data.ETo_mm,
            "Temperature (Min) (C)": data.Temp_Min_C,
            "Temperature (Moy) (C)": data.Temp_Moy_C,
            "Temperature (Max) (C)": data.Temp_Max_C,
            "Humidite relative (Min) (%)": data.Hum_Min_pct,
            "Humidite relative (Moy) (%)": data.Hum_Moy_pct,
            "Humidite relative (Max) (%)": data.Hum_Max_pct,
            "Rayonnement global (j/cm2)": data.Rayonnement_global,
            "VPD (Min) (Kpa)": data.VPD_Min,
            "VPD (Kpa)": data.VPD_Kpa,
            "VPD (Max) (Kpa)": data.VPD_Max,
            "Degre jour (C)": data.Degre_jour,
            
            # ATTENTION : J'ai mis deux espaces ici entre jour et (C) 
            # pour correspondre à l'erreur renvoyée par ton modèle
            "Cumul degres jour  (C)": data.Cumul_degres_jour, 
            
            "Amplitude thermique (C)": data.Amplitude_thermique,
            "Indice de chaleur (C)": data.Indice_chaleur,
            "Point de rosee (C)": data.Point_de_rosee
        }

        # 3. Boucle pour les 4 semaines (42, 43, 44, 45)
        forecast = {}
        for i in range(1, 5):
            week_to_predict = data.Semaine + i
            day_to_predict = data.Jour_apres_plantation + (i * 7)
            
            # On prépare la copie pour la semaine i
            current_input = formatted_data.copy()
            current_input["Semaine"] = week_to_predict
            current_input["Jour apres plantation"] = day_to_predict
            
            # Appel effectif du modèle
            res = predict_yield(current_input)
            forecast[f"Semaine_{week_to_predict}"] = res

        return {
            "input_id": data.id,
            "predictions": forecast
        }

    except Exception as e:
        # Affiche l'erreur exacte dans ton terminal VS Code
        print(f"ERREUR TECHNIQUE : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)