"""
models.py

Définit le modèle de données User exposé par l’API (schéma Pydantic).

Fonctionnalités :
- Structure et validation des données utilisateur retournées par l’API
- Utilisé comme réponse pour la route /users/{login}

Champs principaux :
- login : identifiant GitHub
- id : identifiant numérique unique
- created_at : date de création du compte
- bio : biographie de l’utilisateur
- url : URL du profil GitHub
- avatar : URL de l’avatar GitHub
"""

from pydantic import BaseModel

# Modèle utilisateur exposé par l’API

class User(BaseModel):
    login: str         # Identifiant GitHub
    id: int           # ID numérique unique
    created_at: str   # Date de création du compte (format ISO)
    bio: str | None = None  # Biographie (optionnelle)
    url: str          # URL du profil GitHub
    avatar: str       # URL de l’avatar
