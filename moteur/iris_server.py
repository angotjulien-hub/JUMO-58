from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import os

app = Flask(__name__)
CORS(app) # Autorise les requêtes entre le HTML et le Serveur

# Configuration des chemins
LOG_FILE = "referentiel/flux_live_2026.json"
STATS_FILE = "web_stats.json"
AUDIT_FILE = "referentiel/audit_performance.csv"

# Initialisation des dossiers
if not os.path.exists('referentiel'):
    os.makedirs('referentiel')

def calculer_alerte(retard_sec, is_manoeuvre):
    if is_manoeuvre: return "⚠️ MANOEUVRE EN COURS"
    if retard_sec > 600: return "⚠️ RETARD CRITIQUE - COUPLAGE"
    return None

@app.route('/update_position', methods=['POST'])
def update_position():
    data = request.json
    pol = data.get('pol')
    lat = data.get('lat')
    lon = data.get('lon')
    speed = data.get('speed', 0)
    is_manoeuvre = data.get('manoeuvre', False)
    
    # Simulation d'un retard pour l'exemple (à lier à ton TM plus tard)
    retard_sec = 125 
    timestamp = datetime.datetime.now().isoformat()
    
    info_bus = {
        "timestamp": timestamp,
        "voiture": pol,
        "lat": float(lat),
        "lon": float(lon),
        "vitesse": round(speed * 3.6, 1),
        "manoeuvre": is_manoeuvre,
        "retard_sec": retard_sec,
        "alerte": calculer_alerte(retard_sec, is_manoeuvre)
    }

    # 1. Mise à jour du Flux Live (Historique)
    flux = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try: flux = json.load(f)
            except: flux = []
    flux.append(info_bus)
    with open(LOG_FILE, "w") as f:
        json.dump(flux[-50:], f, indent=4)

    # 2. Mise à jour de web_stats.json pour le PCC et le Hub
    # On gère ici une liste de bus actifs
    stats = {"last_update": datetime.datetime.now().strftime("%H:%M:%S"), "bus_positions": []}
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            try: stats = json.load(f)
            except: pass
    
    # Mise à jour ou ajout du bus dans la liste active
    found = False
    for i, b in enumerate(stats.get('bus_positions', [])):
        if b['id'] == pol:
            stats['bus_positions'][i] = {
                "id": pol, "lat": lat, "lng": lon, 
                "eid": round(retard_sec/60, 1), "intervalle": 5, # Intervalle fixe pour test
                "manoeuvre": is_manoeuvre
            }
            found = True
    if not found:
        stats['bus_positions'].append({"id": pol, "lat": lat, "lng": lon, "eid": 2.1, "intervalle": 5})

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

    return jsonify({"status": "received", "bus": pol}), 200

if __name__ == '__main__':
    print("🚀 SERVEUR IRIS 58 DÉMARRÉ SUR http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
