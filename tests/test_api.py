"""
test_api.py

Tests automatisés pour l'API FastAPI exposant les utilisateurs GitHub.

Ce fichier vérifie :
- L'accessibilité publique de la route /users/ (liste brute, sans auth).
- L'accès protégé et la structure de la route /users/{login} (détail utilisateur, nécessite authentification).
- La gestion du cas utilisateur non trouvé (404).
- Le fonctionnement de la recherche protégée (/users/search?q=...).

Chaque test s'appuie sur les données extraites et filtrées, et vérifie la cohérence des réponses (présence des champs, statut HTTP, etc).

Prérequis :
    - L'API doit être correctement configurée (données présentes, variable API_ACCESS_TOKEN définie).
    - Les scripts d'extraction et de filtrage doivent avoir été exécutés.
"""
import os
import pytest
from fastapi.testclient import TestClient
from api.main import app

# Création d'un client de test pour l'application FastAPI
client = TestClient(app)

# Identifiants pour l'authentification HTTP Basic (admin/token)
USERNAME = "admin"
PASSWORD = os.getenv("API_ACCESS_TOKEN")
if PASSWORD is None:
    raise RuntimeError("API_ACCESS_TOKEN doit être défini dans l'environnement pour exécuter les tests.")

def basic_auth():
    """Retourne un tuple (username, password) pour l'authentification basique."""
    return (USERNAME, PASSWORD)

def test_get_users_public():
    """
    Teste que la route /users/ est accessible sans authentification
    et retourne bien une liste d'utilisateurs.
    """
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user_by_login():
    """
    Teste la récupération détaillée d'un utilisateur via /users/{login} (auth requise).
    Vérifie la présence de tous les champs attendus dans la réponse.
    """
    # On récupère la liste publique
    response = client.get("/users/")
    users = response.json()
    if users:
        login = users[0]["login"]
        # On teste la route protégée (détail)
        response_user = client.get(f"/users/{login}", auth=basic_auth())
        assert response_user.status_code == 200
        data = response_user.json()
        assert data["login"] == login
        # Vérifie la présence des champs attendus
        for field in ["id", "created_at", "bio", "url", "avatar"]:
            assert field in data
    else:
        pytest.skip("No users available for testing.")

def test_user_not_found():
    """
    Teste la gestion du cas où un utilisateur inexistant est demandé.
    Doit retourner une 404.
    """
    response = client.get("/users/thisuserdoesnotexist123", auth=basic_auth())
    assert response.status_code == 404

def test_search_users():
    """
    Teste la recherche d'utilisateurs protégée (/users/search?q=...)
    Vérifie que la recherche retourne bien des utilisateurs dont le login contient la requête.
    """
    response = client.get("/users/",)
    users = response.json()
    if users:
        query = users[0]["login"][:3]
        response_search = client.get(f"/users/search?q={query}", auth=basic_auth())
        assert response_search.status_code == 200
        results = response_search.json()
        assert isinstance(results, list)
        assert any(query.lower() in user["login"].lower() for user in results)
    else:
        pytest.skip("No users available for testing.")
