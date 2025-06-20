"""
main.py

Point d'entrée de l'API FastAPI pour le projet GitHub Users.

Fonctionnalités principales :
- Chargement de la configuration et des variables d'environnement.
- Inclusion des routes REST définies dans api/routes.py.
- Page d'accueil HTML moderne avec liens rapides (/, /users/, /docs).
- Gestion de la requête favicon.ico pour éviter les erreurs 404 dans les logs.

Usage :
    uvicorn api.main:app --reload

Prérequis :
    - Dépendances Python (voir requirements.txt)
    - Fichier .env avec GITHUB_TOKEN et API_ACCESS_TOKEN
"""

import os
import sys
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse, Response

# Ajouter le chemin du dossier parent pour accéder à extract_users
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract_users import extract_users
from api.routes import router  # 👈 Import des routes

# Chargement des variables d'environnement (.env)
load_dotenv()
print("[🐞] GITHUB_TOKEN dans FastAPI :", os.getenv("GITHUB_TOKEN"))

# Création de l'application FastAPI
app = FastAPI()

# Inclusion des routes définies dans api/routes.py
app.include_router(router)

# Page d'accueil HTML stylée avec liens rapides et instructions
@app.get("/", response_class=HTMLResponse)
def read_root():
    print("[INFO] Accès à la page d'accueil de l'API (/)")
    return """
    <html>
        <head>
            <title>Bienvenue sur l'API GitHub Users</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f7f7f7; color: #222; margin: 0; padding: 0; }
                .navbar { background: #e3f0fc; padding: 16px 0 12px 0; text-align: center; border-bottom: 1px solid #b3d4fc; }
                .navbar a { color: #2176c7; text-decoration: none; font-weight: bold; margin: 0 18px; font-size: 1.08em; transition: color 0.2s; }
                .navbar a:hover { color: #174e85; text-decoration: underline; }
                .container { max-width: 600px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px #0001; padding: 32px; }
                h1 { color: #2d72d9; }
                a { text-decoration: none; }
                .quick { background: #f0f4fa; border-radius: 8px; padding: 12px; margin-top: 18px; font-size: 0.98em; }
            </style>
        </head>
        <body>
            <div class="navbar">
                <a href="/">Accueil</a>
                <a href="/users/">Liste des utilisateurs</a>
                <a href="/docs">Swagger UI</a>
            </div>
            <div class="container">
                <h1>Bienvenue sur l'API GitHub Users </h1>
                <p>Cette API permet d'explorer des utilisateurs GitHub extraits et filtrés.</p>
                <ul>
                    <li>🔓 <b>GET</b> <code>/users/</code> — Liste tous les utilisateurs (public)</li>
                    <li>🔐 <b>GET</b> <code>/users/search?q=...</code> — Recherche (auth requise)</li>
                    <li>🔐 <b>GET</b> <code>/users/&lt;login&gt;</code> — Détail utilisateur (auth requise)</li>
                </ul>
                <div class="quick">
                    <b>Documentation interactive :</b><br>
                    <a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a>
                </div>
                <div class="quick" style="margin-top:18px;">
                    <b>Test rapide :</b><br>
                    <code>curl http://127.0.0.1:8000/users/</code>
                </div>
            </div>
        </body>
    </html>
    """

# Route pour ignorer la requête favicon.ico (évite le 404 dans les logs)
@app.get("/favicon.ico")
def ignore_favicon():
    return Response(status_code=204)