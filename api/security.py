"""
security.py

Gère l'authentification HTTP Basic pour l'API GitHub Users (FastAPI).

Fonctionnalités :
- Chargement du mot de passe d'accès API depuis les variables d'environnement (.env)
- Vérification des identifiants reçus via HTTP Basic Auth
- Refus explicite (401) si l'utilisateur ou le mot de passe est incorrect

Prérequis :
    - La variable d'environnement API_ACCESS_TOKEN doit être définie dans .env
    - Le nom d'utilisateur attendu est "admin"
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis un fichier .env
load_dotenv()

# Initialisation de la sécurité HTTP Basic
security = HTTPBasic()

# Définir les identifiants autorisés (ici : admin + mot de passe depuis .env)
try:
    AUTHORIZED_USERS = {
        "admin": os.environ["API_ACCESS_TOKEN"]
    }
except KeyError:
    raise RuntimeError("API_ACCESS_TOKEN n'est pas défini dans le fichier .env ou l'environnement.")


def check_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Vérifie les identifiants de l'utilisateur reçus via HTTP Basic Auth.
    Retourne le nom d'utilisateur si authentifié avec succès.
    Lève une exception HTTP 401 en cas d'échec.
    """
    username = credentials.username
    password = credentials.password

    # Vérifie si le nom d'utilisateur est autorisé
    if username in AUTHORIZED_USERS:
        valid_password = AUTHORIZED_USERS[username]
        # Compare les mots de passe de façon sécurisée
        if secrets.compare_digest(password, valid_password):
            return username

    # Si l'authentification échoue, lève une erreur 401
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Basic"},
    )
