"""
filtered_users.py

Script de filtrage et de nettoyage des utilisateurs extraits :
- Charge les utilisateurs depuis data/users.json (généré par extract_users.py).
- Supprime les doublons (clé unique : id).
- Applique des filtres supplémentaires :
    - Bio non vide
    - Avatar non vide
    - Date de création après 2015-01-01
- Sauvegarde le résultat dans data/filtered_users.json.

Usage :
    python filtered_users.py

Prérequis :
    - Avoir exécuté extract_users.py au préalable
    - Dépendances Python (voir requirements.txt)
"""

import json
import os
from datetime import datetime

# Fonction pour charger les utilisateurs depuis un fichier JSON
# Vérifie la présence des champs essentiels dans chaque utilisateur

def load_users(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        users = json.load(f)
    # Vérification simple structure : au moins un champ login et id
    for u in users:
        if not all(k in u for k in ("login", "id", "created_at", "avatar_url", "bio")):
            raise ValueError("Format utilisateur incorrect, champs manquants")
    return users

# Fonction pour supprimer les doublons d'utilisateurs (basé sur l'id)
def remove_duplicates(users):
    unique = {}
    for user in users:
        unique[user["id"]] = user  # la clé unique est 'id', écrase doublons
    return list(unique.values())

# Fonction pour filtrer les utilisateurs selon plusieurs critères
def filter_users(users):
    filtered = []
    cutoff_date = datetime(2015, 1, 1)
    for u in users:
        bio = u.get("bio")
        avatar = u.get("avatar_url")
        created_at_str = u.get("created_at")

        # On ne garde que les utilisateurs avec une bio non vide
        if not bio or bio.strip() == "":
            continue
        # On ne garde que les utilisateurs avec un avatar non vide
        if not avatar or avatar.strip() == "":
            continue
        # On ne garde que les utilisateurs créés après 2015-01-01
        try:
            created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            continue
        if created_at < cutoff_date:
            continue
        
        # Si tous les critères sont remplis, on ajoute l'utilisateur filtré
        filtered.append({
            "login": u["login"],
            "id": u["id"],
            "created_at": u["created_at"],
            "avatar_url": u["avatar_url"],
            "bio": u["bio"]
        })
    return filtered

# Fonction pour sauvegarder les utilisateurs filtrés dans un fichier JSON
def save_filtered_users(users, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# Fonction principale du script
def main():
    input_path = "data/users.json"
    output_path = "data/filtered_users.json"

    try:
        # Chargement des utilisateurs extraits
        users = load_users(input_path)
        before_dedup = len(users)
        # Suppression des doublons
        users_no_dups = remove_duplicates(users)
        after_dedup = len(users_no_dups)
        # Application des filtres
        filtered_users = filter_users(users_no_dups)
        after_filter = len(filtered_users)

        # Sauvegarde du résultat
        save_filtered_users(filtered_users, output_path)

        print(f"\n✅ Traitement terminé.")
        print(f"👥 Utilisateurs chargés : {before_dedup}")
        print(f"♻️  Doublons supprimés : {before_dedup - after_dedup}")
        print(f"🔍 Utilisateurs filtrés : {after_filter}")
        print(f"📁 Données sauvegardées dans : {output_path}\n")

    except Exception as e:
        print(f"\n❌ Erreur lors du traitement : {e}\n")

# Point d'entrée du script
if __name__ == "__main__":
    main()
