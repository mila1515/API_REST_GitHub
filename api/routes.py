"""
routes.py

Définit les routes principales de l'API GitHub Users (FastAPI).

Fonctionnalités :
- Route publique pour lister tous les utilisateurs extraits (GET /users/)
- Route protégée pour rechercher des utilisateurs par login (GET /users/search?q=...)
- Route protégée pour obtenir le détail d'un utilisateur par login (GET /users/{login})
- Chargement des données filtrées depuis data/filtered_users.json
- Authentification HTTP Basic sur les routes sensibles

Prérequis :
    - Les fichiers data/users.json et data/filtered_users.json doivent être générés au préalable
    - L'authentification est gérée via api/security.py
"""

from fastapi import APIRouter, Depends, HTTPException
from api.models import User
from api.security import check_auth
import json
import traceback

router = APIRouter()

# Chargement des utilisateurs filtrés depuis JSON au démarrage du module
try:
    with open("data/filtered_users.json", encoding="utf-8") as f:
        users_data = json.load(f)
    users_dict = {user["login"]: user for user in users_data}
except FileNotFoundError:
    users_data = []
    users_dict = {}

# 🔓 Route publique : retourne tous les utilisateurs extraits depuis data/users.json
@router.get("/users/", summary="Lister tous les utilisateurs (non filtrés)")
def get_users():
    """
    Retourne la liste brute des utilisateurs extraits (public, pas d'authentification).
    """
    try:
        with open("data/users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
        return users
    except Exception as e:
        return {"error": str(e)}

# 🔐 Route protégée : recherche d'utilisateurs par login (query string)
@router.get("/users/search")
def search_users(q: str, credentials=Depends(check_auth)):
    """
    Recherche les utilisateurs dont le login contient la chaîne q (authentification requise).
    """
    print(f"Recherche pour: {q}")
    try:
        results = [user for user in users_dict.values() if "login" in user and q.lower() in user["login"].lower()]
        print(f"Nombre de résultats: {len(results)}")
        return results
    except Exception as e:
        traceback.print_exc()  # Affiche la trace complète de l'erreur
        return {"error": str(e)}

# 🔐 Route protégée : obtenir un utilisateur par login exact
@router.get("/users/{login}", response_model=User, summary="Obtenir un utilisateur", description="Retourne les détails d'un utilisateur par son login exact.")
def get_user(login: str, credentials=Depends(check_auth)):
    """
    Retourne les détails d'un utilisateur (authentification requise).
    Adapte les clés pour correspondre au modèle User attendu.
    """
    try:
        login_lower = login.lower()
        user = next((u for u in users_dict.values() if u.get("login", "").lower() == login_lower), None)
        if user is None:
            raise HTTPException(status_code=404, detail=f"Utilisateur '{login}' non trouvé.")
        # Adaptation des clés pour correspondre au modèle User attendu
        user_mapped = {
            "login": user.get("login"),
            "id": user.get("id"),
            "created_at": user.get("created_at"),
            "bio": user.get("bio"),
            "url": user.get("html_url", ""),          # <- attention ici
            "avatar": user.get("avatar_url", ""),    # <- et ici
        }
        return user_mapped
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
