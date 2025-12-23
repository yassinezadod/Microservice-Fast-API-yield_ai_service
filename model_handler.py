import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import os

# --- CONFIGURATION ET CHEMINS ---
MODEL_PATH = "champion_model.pkl"
DATA_PATH = "Data.csv"

# Chargement du modèle sauvegardé
model = joblib.load(MODEL_PATH)

# Initialisation des objets globaux
scaler = StandardScaler()
le_variete = LabelEncoder()
le_phase = LabelEncoder()
duree_reference = {}

def get_feature_list():
    """Retourne la liste exacte et ordonnée des 33 features du modèle"""
    return [
        'Semaine', 'Vitesse de maturation', 'variete_encoded', 'ETo (mm)',
        'Temperature (Min) (C)', 'Temperature (Moy) (C)', 'Temperature (Max) (C)',
        'Humidite relative (Min) (%)', 'Humidite relative (Moy) (%)',
        'Humidite relative (Max) (%)', 'Rayonnement global (j/cm2)', 
        'Degre jour (C)', 'Cumul degres jour  (C)', 'Amplitude thermique (C)', 
        'Indice de chaleur (C)', 'Point de rosee (C)', 'duree_plantation', 
        'progres', 'progres_sin', 'progres_cos', 'progres_x_temp', 
        'progres_x_humidite', 'semaine_sin', 'semaine_cos', 
        'phase_croissance_encoded', 'stress_thermique', 'stress_hydrique', 
        'confort_thermique', 'deficit_vapeur', 'efficacite_maturation', 
        'energie_cumulative', 'ratio_temp_humidite', 'efficience_ETo'
    ]

def create_features(df, is_init=False):
    """Logique de Feature Engineering (33 variables)"""
    df = df.copy()
    
    # Nettoyage strict de la variété (supprime les .0)
    df['variete'] = pd.to_numeric(df['variete'], errors='coerce').fillna(0).astype(int).astype(str)
    
    # Calcul ou récupération de la durée de plantation
    if is_init:
        duree_par_var = df.groupby('variete')['Jour apres plantation'].max()
        df['duree_plantation'] = df['variete'].map(duree_par_var)
    else:
        df['duree_plantation'] = df['variete'].map(duree_reference).fillna(df['Jour apres plantation'])

    # Progrès de la culture
    df['progres'] = (df['Jour apres plantation'] / df['duree_plantation']).clip(0, 1)

    # Features cycliques
    df['semaine_sin'] = np.sin(2 * np.pi * df['Semaine'] / 52)
    df['semaine_cos'] = np.cos(2 * np.pi * df['Semaine'] / 52)
    df['progres_sin'] = np.sin(2 * np.pi * df['progres'])
    df['progres_cos'] = np.cos(2 * np.pi * df['progres'])

    # Détermination des phases
    def get_phase(p):
        if p <= 0.25: return 'germination'
        elif p <= 0.5: return 'croissance_vegetative'
        elif p <= 0.75: return 'floraison'
        else: return 'fructification'
    df['phase_croissance'] = df['progres'].apply(get_phase)

    # Indices de stress et confort
    df['stress_thermique'] = (df['Temperature (Max) (C)'] > 35).astype(int)
    df['stress_hydrique'] = (df['Humidite relative (Min) (%)'] < 60).astype(int)
    df['confort_thermique'] = 100 - abs(df['Temperature (Moy) (C)'] - 25)
    df['deficit_vapeur'] = df['Temperature (Moy) (C)'] - df['Point de rosee (C)']

    # Ratios agronomiques avancés
    df['efficacite_maturation'] = df['Vitesse de maturation'] / (df['progres'] + 0.01)
    df['energie_cumulative'] = df['Rayonnement global (j/cm2)'] * df['Cumul degres jour  (C)']
    df['progres_x_temp'] = df['progres'] * df['Temperature (Moy) (C)']
    df['progres_x_humidite'] = df['progres'] * df['Humidite relative (Moy) (%)']
    df['ratio_temp_humidite'] = df['Temperature (Moy) (C)'] / (df['Humidite relative (Moy) (%)'] + 0.1)
    df['efficience_ETo'] = df['ETo (mm)'] / (df['Temperature (Moy) (C)'] + 0.1)

    return df

def init_handler():
    """Initialise le service en entraînant les scalers/encoders sur Data.csv"""
    global duree_reference, scaler, le_variete, le_phase
    
    if not os.path.exists(DATA_PATH):
        print(f"❌ Erreur critique : {DATA_PATH} introuvable.")
        return

    df = pd.read_csv(DATA_PATH, sep=',', encoding='utf-8')
    
    # Nettoyage initial
    df['variete'] = pd.to_numeric(df['variete'], errors='coerce').fillna(0).astype(int).astype(str)
    
    # Mémorisation des durées max par variété
    duree_reference = df.groupby('variete')['Jour apres plantation'].max().to_dict()
    
    # Feature Engineering complet
    df_feat = create_features(df, is_init=True)
    
    # Entraînement des Encoders (FIT)
    le_variete.fit(df_feat['variete'])
    le_phase.fit(df_feat['phase_croissance'])
    
    # Encodage pour le fit du scaler
    df_feat['variete_encoded'] = le_variete.transform(df_feat['variete'])
    df_feat['phase_croissance_encoded'] = le_phase.transform(df_feat['phase_croissance'])
    
    # Entraînement du Scaler (FIT UNIQUE) sur les 33 colonnes
    features_to_use = get_feature_list()
    scaler.fit(df_feat[features_to_use])
    
    print("✅ model_handler initialisé : Références apprises depuis Data.csv.")

def predict_yield(input_dict):
    """Transforme une entrée unique et retourne la prédiction de rendement"""
    # 1. Chargement dans un DataFrame d'une ligne
    df_raw = pd.DataFrame([input_dict])
    
    # 2. Feature Engineering (utilise duree_reference)
    df_feat = create_features(df_raw, is_init=False)
    
    # 3. Encodage avec les objets déjà entraînés (TRANSFORM uniquement)
    df_feat['variete_encoded'] = le_variete.transform(df_feat['variete'])
    df_feat['phase_croissance_encoded'] = le_phase.transform(df_feat['phase_croissance'])

    # 4. Sélection des 33 features
    X = df_feat[get_feature_list()]
    
    # 5. Normalisation SANS ré-entraînement (TRANSFORM uniquement)
    X_scaled = scaler.transform(X)

    # 6. Prédiction finale
    prediction = model.predict(X_scaled)
    return round(float(prediction[0]), 3)

# Lancement automatique de l'initialisation au chargement du script
init_handler()