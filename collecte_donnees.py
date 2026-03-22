import json
from datetime import datetime

class IrisCollector:
    def __init__(self):
        self.data = self.load_db()

    def load_db(self):
        with open('iris_master_data.json', 'r') as f:
            return json.load(f)

    def get_eid(self, tv_id, stop_code):
        # 1. Détecter le type de jour
        day_type = "Semaine" # Logique à automatiser selon la date
        
        # 2. Chercher la mission
        mission = self.data.get(day_type, {}).get(str(tv_id))
        if not mission: return "TV INCONNU"

        # 3. Calculer l'écart
        theo = mission['stops'].get(stop_code)
        if not theo: return "ARRET INCONNU"
        
        now = datetime.now().strftime("%H:%M:%S")
        fmt = "%H:%M:%S"
        diff = (datetime.strptime(now, fmt) - datetime.strptime(theo, fmt)).total_seconds() / 60
        
        return round(diff, 1) # Retourne l'EID en minutes (ex: +3.5)
