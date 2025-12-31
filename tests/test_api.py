import os
import pytest
from httpx import AsyncClient
from dotenv import load_dotenv

# Charger les variables du .env
load_dotenv()

LARAVEL_URL = os.getenv("LARAVEL_SYNC_URL")
VALID_KEY = os.getenv("LARAVEL_SYNC_KEY")

@pytest.mark.asyncio
async def test_fetch_laravel_data():
    """
    Test asynchrone pour vérifier que l'API Laravel 
    renvoie les données avec succès.
    """
    headers = {
        "X-Internal-Sync-Key": VALID_KEY,
        "Accept": "application/json"
    }

    # Utilisation de AsyncClient pour simuler l'appel asynchrone
    async with AsyncClient() as client:
        response = await client.get(LARAVEL_URL, headers=headers)

    # Vérifications
    assert response.status_code == 200, f"Erreur de connexion: {response.status_code}"
    
    json_data = response.json()
    assert json_data["success"] is True
    assert "data" in json_data
    assert isinstance(json_data["data"], list)

    # Affichage pour le mode -s de pytest
    print(f"\n✅ Connexion établie avec Laravel")
    print(f"✅ {len(json_data['data'])} analyses récupérées avec succès")