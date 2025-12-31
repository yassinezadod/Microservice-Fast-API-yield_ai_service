import os
import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from database import get_history_collection


load_dotenv()

async def sync_data_to_mongodb():
    print(f"\n[🚀 SYNC] Démarrage de la synchronisation à {datetime.now().strftime('%H:%M:%S')}")

    url = os.getenv("LARAVEL_SYNC_URL")
    key = os.getenv("LARAVEL_SYNC_KEY")
    
    headers = {
        "X-Internal-Sync-Key": key,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return {"error": f"Laravel error: {response.status_code}"}

            results = response.json().get('data', [])
            collection = get_history_collection()
            new_entries = 0

            for record in results:
                # Récupération des données de base
                variete = record['variete']
                prediction = record['prediction']
                input_data = prediction['input_data']
                current_week_info = input_data['current_week_data']
                start_week = current_week_info['Semaine']

                # Boucle sur les données réelles saisies par l'utilisateur
                for detail in record['comparaison_details']:
                    target_week = detail['semaine']
                    diff = target_week - start_week
                    s_key = f"S{diff}" # S1, S2, S3 ou S4
                    
                    climate = input_data['predictions_input'].get(s_key)
                    if not climate: continue

                    # Construction du document final formaté (33 features)
                    doc = {
                        "Semaine": target_week,
                        "Jour apres plantation": current_week_info['Jour_apres_plantation'] + (diff * 7),
                        "Vitesse de maturation": current_week_info['Vitesse_de_maturation'],
                        "variete": int(variete),
                        "Rendement (t/ha)": detail['reel'], # La valeur réelle !
                        "ETo (mm)": climate['ETo_mm'],
                        "Temperature (Min) (C)": climate['Temp_Min_C'],
                        "Temperature (Moy) (C)": climate['Temp_Moy_C'],
                        "Temperature (Max) (C)": climate['Temp_Max_C'],
                        "Humidite relative (Min) (%)": climate['Hum_Min_pct'],
                        "Humidite relative (Moy) (%)": climate['Hum_Moy_pct'],
                        "Humidite relative (Max) (%)": climate['Hum_Max_pct'],
                        "Rayonnement global (j/cm2)": climate['Rayonnement_global'],
                        "VPD (Min) (Kpa)": climate['VPD_Min'],
                        "VPD (Kpa)": climate['VPD_Kpa'],
                        "VPD (Max) (Kpa)": climate['VPD_Max'],
                        "Degre jour (C)": climate['Degre_jour'],
                        "Cumul degres jour  (C)": climate['Cumul_degres_jour'],
                        "Amplitude thermique (C)": climate['Amplitude_thermique'],
                        "Indice de chaleur (C)": climate['Indice_chaleur'],
                        "Point de rosee (C)": climate['Point_de_rosee'],
                        "user_id": prediction['user_id'],
                        "provenance": "laravel_sync",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }

                    # Check doublon avant insertion
                    query = {"variete": doc["variete"], "Semaine": doc["Semaine"], "Rendement (t/ha)": doc["Rendement (t/ha)"]}
                    if not collection.find_one(query):
                        collection.insert_one(doc)
                        new_entries += 1
            print(f"[✅ SYNC] Terminée. Nouvelles entrées ajoutées : {new_entries}")
            return {"status": "success", "added": new_entries}

        except Exception as e:
            return {"error": str(e)}
        
if __name__ == "__main__":
    print("🚀 Lancement de la synchronisation manuelle...")
    result = asyncio.run(sync_data_to_mongodb())
    print(f"📊 Résultat : {result}")