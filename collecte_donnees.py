import os
import time
import json
import pandas as pd # Utilisation de pandas pour la performance de calcul
from datetime import datetime

# --- CONFIGURATION IRIS ---
CONFIG_PATH = "iris_config.json"
MASTER_DATA_PATH = "iris_master_data.json"
LOG_DIR = "rapports"

class IrisCollector:
    def __init__(self):
        self.load_config()
        self.load_master_data()
        if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

    def load_config(self):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def load_master_data(self):
        """Charge la base de données générée à partir de tes CSV"""
        if os.path.exists(MASTER_DATA_PATH):
            with open(MASTER_DATA_PATH, 'r', encoding='utf-8') as f:
                self.master_data = json.load(f)
        else:
            print("⚠️ Base horaire manquante. Lancez le parser CSV d'abord.")
            self.master_data = {}

    def get_current_day_type(self):
        """Détermine si on est en Semaine, Samedi ou Dimanche"""
        dow = datetime.now().weekday()
        if dow == 5: return "Samedi"
        if dow == 6: return "Dimanche"
        return "Semaine"

    def calculer_eid(self, tv_id, stop_id, heure_reelle):
        """Calcule l'écart entre le théorique (CSV) et le réel (GPS)"""
        day_type = self.get_current_day_type()
        try:
            # Récupération de l'horaire théorique dans le dictionnaire master_data
            mission = self.master_data.get(day_type, {}).get(str(tv_id))
            if not mission: return None
            
            theo_str = next(s['t'] for s in mission['stops'] if s['id'] == stop_id)
            fmt = "%H:%M:%S"
            t_theo = datetime.strptime(theo_str, fmt)
            t_reel = datetime.strptime(heure_reelle, fmt)
            
            diff = (t_reel - t_theo).total_seconds() / 60
            return diff # Retourne l'écart en minutes
        except Exception:
            return 0

    def scanner_flotte(self):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛰️ SCAN IRIS LIGNE 58 - MODE {self.get_current_day_type().upper()}")
        
        # Simulation de récupération des positions (Via API ou PeerJS)
        # Dans la version réelle, on ferait : requests.get(API_URL)
        flotte_active = [
            {"pol": "8501", "tv": "44298328", "pos": [48.858, 2.341], "stop": "CTL"},
            {"pol": "8544", "tv": "44298356", "pos": [48.830, 2.306], "stop": "VM"}
        ]

        rapport = []
        for bus in flotte_active:
            h_now = datetime.now().strftime("%H:%M:%S")
            eid = self.calculer_eid(bus['tv'], bus['stop'], h_now)
            
            status = "✅ NOMINAL" if eid and abs(eid) < 3 else "⚠️ DÉCALÉ"
            print(f"   > Unité P{bus['pol']} | TV {bus['tv']} | EID: {eid:+.1f} min | {status}")
            
            rapport.append({
                "timestamp": h_now,
                "police": bus['pol'],
                "tv": bus['tv'],
                "eid": eid,
                "status": status
            })
        
        self.archiver_data(rapport)

    def archiver_data(self, data):
        filename = f"{LOG_DIR}/regul_{datetime.now().strftime('%Y%m%d')}.json"
        # On ajoute au fichier existant
        current_logs = []
        if os.path.exists(filename):
            with open(filename, 'r') as f: current_logs = json.load(f)
        
        current_logs.extend(data)
        with open(filename, 'w') as f:
            json.dump(current_logs, f, indent=4)

# --- BOUCLE DE RÉGULATION ---
if __name__ == "__main__":
    iris = IrisCollector()
    try:
        while True: # Surveillance infinie
            iris.scanner_flotte()
            time.sleep(30) # Fréquence de scan de 30 secondes pour une précision RATP
    except KeyboardInterrupt:
        print("\n🛑 Système IRIS mis en veille.")
