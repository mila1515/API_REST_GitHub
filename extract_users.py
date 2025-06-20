"""
extract_users.py

Script d'extraction d'utilisateurs GitHub :
- Se connecte à l'API GitHub avec un token personnel.
- Récupère des utilisateurs par pagination, en respectant les quotas de l'API.
- Pour chaque utilisateur, récupère les détails (login, id, avatar, date de création, bio).
- Filtre les utilisateurs selon plusieurs critères (date, avatar, bio).
- Sauvegarde le résultat dans data/users.json.

Usage :
    python extract_users.py --max-users 60

Prérequis :
    - Dépendances Python (voir requirements.txt)
    - Fichier .env avec GITHUB_TOKEN
"""

# ==== Import des bibliothèques nécessaires ====

import requests
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
import argparse

# ==== Étape 2 : Chargement du token GitHub depuis .env ====
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("[❌] Token GitHub non trouvé dans .env (GITHUB_TOKEN).")
    exit(1)

# Préparation des headers pour l'authentification à l'API GitHub
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

BASE_URL = "https://api.github.com"
USERS_ENDPOINT = f"{BASE_URL}/users"

# === Création dossier pour sauvegarder les données ===
os.makedirs("data", exist_ok=True)

# Fonction pour gérer le quota de l'API GitHub (attend si quota épuisé)
def handle_rate_limit(response):
    """
    Étape 3 : Gestion des quotas de l'API GitHub.
    Pause si quota épuisé, en fonction des headers.
    """
    remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
    reset_time = int(response.headers.get("X-RateLimit-Reset", time.time()))
    if remaining == 0:
        wait_time = reset_time - time.time()
        if wait_time > 0:
            print(f"[⏳] Quota API GitHub épuisé. Pause jusqu'à {datetime.fromtimestamp(reset_time)} ({int(wait_time)}s)...")
            time.sleep(wait_time + 5)

# Fonction pour récupérer les détails d'un utilisateur (login, id, avatar, etc.)
def get_user_details(login):
    """
    Étape 1 : Récupérer les infos détaillées d'un utilisateur via /users/<login>.
    Renvoie un dict avec login, id, avatar_url, created_at, bio ou None si erreur.
    """
    url = f"{USERS_ENDPOINT}/{login}"
    try:
        response = requests.get(url, headers=HEADERS)
        handle_rate_limit(response)

        if response.status_code == 200:
            data = response.json()
            return {
                "login": data["login"],
                "id": data["id"],
                "created_at": data["created_at"],
                "avatar_url": data["avatar_url"],
                "bio": data.get("bio")
            }
        elif response.status_code == 403:
            print(f"[⚠️] 403 Forbidden - quota ou token ? Pause 60s...")
            time.sleep(60)
        elif response.status_code == 429:
            print(f"[⚠️] 429 Too Many Requests - temporisation progressive...")
            time.sleep(10)
        elif 500 <= response.status_code < 600:
            print(f"[⚠️] Erreur serveur {response.status_code}, nouvelle tentative dans 5s...")
            time.sleep(5)
        else:
            print(f"[⚠️] Erreur HTTP {response.status_code} pour utilisateur {login}")
    except Exception as e:
        print(f"[❌] Exception lors de récupération de {login} : {e}")
    return None

# Point de départ pour la pagination (ID utilisateur)
START_SINCE_ID = 30000000

def extract_users(max_users):
    """
    Étape 4 & 5 : Pagination automatique et gestion des erreurs.
    - Récupère max_users utilisateurs en paginant via since=<id>.
    - Filtre utilisateurs créés après 2015, avec avatar_url non vide et bio renseignée.
    """
    users = []
    since_id = START_SINCE_ID
    no_new_user_count = 0  # compteur batches sans ajout utilisateur

    while len(users) < max_users:
        print(f"[🔄] Requête utilisateurs depuis ID {since_id}...")
        try:
            # Récupération d'un batch d'utilisateurs (pagination)
            response = requests.get(f"{USERS_ENDPOINT}?since={since_id}", headers=HEADERS)
            handle_rate_limit(response)

            if response.status_code != 200:
                print(f"[⚠️] Erreur HTTP {response.status_code} sur la requête principale, pause 5s...")
                time.sleep(5)
                continue

            batch = response.json()
            if not batch:
                print("[⚠️] Aucun utilisateur reçu, fin de pagination.")
                break

            new_users_in_batch = 0

            for user in batch:
                if len(users) >= max_users:
                    break

                # Récupérer détails complets utilisateur
                details = get_user_details(user["login"])
                if not details:
                    continue

                # Filtrer selon les critères demandés :
                # - created_at après 2015-01-01
                # - avatar_url non vide
                # - bio renseignée (pas None, pas vide)
                cutoff_date = datetime(2015, 1, 1)
                created_date = datetime.strptime(details["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                if created_date < cutoff_date:
                    print(f"[⏩] {details['login']} ignoré (créé le {created_date.date()}, avant 2015)")
                    continue

                if not details["avatar_url"]:
                    print(f"[⏩] {details['login']} ignoré (avatar_url vide)")
                    continue

                bio = details.get("bio")
                if bio is None or bio.strip() == "":
                    print(f"[⏩] {details['login']} ignoré (bio vide ou non renseignée)")
                    continue

                # Si passe tous les filtres, ajout à la liste
                users.append(details)
                new_users_in_batch += 1
                print(f"[✔️] {details['login']} ajouté.")

            if new_users_in_batch == 0:
                no_new_user_count += 1
                print(f"[⚠️] Aucun nouvel utilisateur ajouté dans ce batch ({no_new_user_count} fois de suite).")
                if no_new_user_count >= 5:
                    print("[⚠️] Arrêt : trop de batches sans ajout.")
                    break
            else:
                no_new_user_count = 0

            # Préparer la prochaine pagination depuis le dernier ID de batch
            since_id = batch[-1]["id"]
            time.sleep(1)  # Petite pause pour ne pas spammer l'API

        except Exception as e:
            print(f"[❌] Exception lors de la requête principale : {e}")
            time.sleep(5)

    return users

# Fonction pour sauvegarder les utilisateurs extraits dans un fichier JSON
def save_users_to_file(users, filename="data/users.json"):
    """
    Étape 6 : Enregistrer les données dans un JSON propre.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    print(f"[💾] {len(users)} utilisateurs enregistrés dans {filename}")

# Point d'entrée du script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extraction utilisateurs GitHub")
    parser.add_argument("--max-users", type=int, default=60, help="Nombre maximum d'utilisateurs à récupérer")
    args = parser.parse_args()

    print(f"[🚀] Début de l'extraction pour {args.max_users} utilisateurs...")
    users = extract_users(args.max_users)
    save_users_to_file(users)
