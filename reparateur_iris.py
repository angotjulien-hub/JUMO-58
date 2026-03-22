import os
import shutil

# 1. Création de la structure propre
folders = ['moteur', 'referentiel', 'archives']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"✅ Dossier {folder} créé.")

# 2. On s'assure que les fichiers HTML critiques sont à la RACINE
html_files = ['index.html', 'pcc_controle.html', 'chauffeur_pro_58.html']
for file in html_files:
    if os.path.exists(file):
        print(f"✨ {file} est bien placé.")
    else:
        print(f"⚠️ {file} manquant à la racine ! Vérifie tes dossiers.")

# 3. Création d'un fichier de données de TEST pour réveiller le PCC
test_data = {
    "last_update": "18:00:00",
    "bus_positions": [
        {"id": "5801", "lat": 48.825, "lng": 2.325, "eid": 0.5, "intervalle": 6, "manoeuvre": False}
    ]
}

import json
with open('web_stats.json', 'w') as f:
    json.dump(test_data, f, indent=4)
    print("        Données de test injectées dans web_stats.json")

print("\n🚀 CONFIGURATION PRÊTE. Tu peux maintenant ouvrir pcc_controle.html")
