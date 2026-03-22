import json
import datetime
import os
import time
import random

class HubReceptionP2P:
    def __init__(self):
        # Chemins des fichiers cibles
        self.log_file = "referentiel/flux_live_2026.json"
        self.web_stats = "web_stats.json"
        self.audit_file = "referentiel/audit_performance.csv"
        
        # S'assurer que le dossier referentiel existe
        if not os.path.exists('referentiel'):
            os.makedirs('referentiel')

    def connecter_machiniste(self, id_voiture, lat, lon, heading, is_manoeuvre, retard_sec=0):
        timestamp = datetime.datetime.now().isoformat()
        
        # Structure de donnée enrichie IRIS 58
        donnee = {
            "timestamp": timestamp,
            "voiture": id_voiture,
            "lat": float(lat),
            "lon": float(lon),
            "cap": heading,
            "manoeuvre": is_manoeuvre,
            "retard_sec": retard_sec,
            "statut": "EN_MANOEUVRE" if is_manoeuvre else "EN_LIGNE",
            "intervalle": random.randint(2, 12) # Simulation de l'intervalle avec le bus précédent
        }
        
        # --- LOGIQUE DE RÉGULATION (COUPLAGE) ---
        # Si retard > 10min ou manoeuvre manuelle, on déclenche l'alerte
        if retard_sec > 600 or is_manoeuvre:
            donnee["alerte"] = "⚠️ PRIORITÉ RÉGULATION - COUPLAGE DÉTECTÉ"
            print(f"!!! ALERTE COUPLAGE SUR VOITURE {id_voiture} !!!")
        
        self._sauvegarder_flux(donnee)
        self._mettre_a_jour_dashboard_web(donnee)
        return donnee

    def _sauvegarder_flux(self, donnee):
        # 1. Mise à jour du JSON Live (Historique court)
        flux = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                try:
                    flux = json.load(f)
                except: flux = []
        
        flux.append(donnee)
        # On garde les 50 dernières positions pour le Hub
        with open(self.log_file, "w") as f:
            json.dump(flux[-50:], f, indent=4)

        # 2. Historisation CSV pour l'Audit de Performance
        file_exists = os.path.exists(self.audit_file)
        with open(self.audit_file, "a") as f:
            if not file_exists or os.stat(self.audit_file).st_size == 0:
                f.write("Date;Voiture;Lat;Lon;Cap;Manoeuvre;Retard\n")
            f.write(f"{donnee['timestamp']};{donnee['voiture']};{donnee['lat']};{donnee['lon']};{donnee['cap']};{donnee['manoeuvre']};{donnee['retard_sec']}\n")

    def _mettre_a_jour_dashboard_web(self, derniere_donnee):
        """ Crée le fichier web_stats.json utilisé par index.html et pcc_controle.html """
        stats = {
            "last_update": datetime.datetime.now().strftime("%H:%M:%S"),
            "ponctualite": random.randint(90, 98), # À remplacer par ton calcul réel
            "eid_moyen": round(derniere_donnee['retard_sec'] / 60, 1),
            "bus_positions": [
                {
                    "id": derniere_donnee['voiture'],
                    "lat": derniere_donnee['lat'],
                    "lng": derniere_donnee['lon'],
                    "eid": round(derniere_donnee['retard_sec'] / 60, 1),
                    "intervalle": derniere_donnee['intervalle']
                }
            ]
        }
        with open(self.web_stats, 'w') as f:
            json.dump(stats, f, indent=4)

# --- BOUCLE DE SIMULATION (Pour tester sans chauffeurs réels) ---
if __name__ == "__main__":
    iris_hub = HubReceptionP2P()
    print("🛰️ MOTEUR DE COLLECTE P2P - IRIS 58 ACTIVÉ")
    
    # Simulation d'un bus qui avance vers Vanves-Michelet
    start_lat, start_lon = 48.8475, 2.3301 # Secteur Fleurus
    
    while True:
        # On simule un léger mouvement et un retard de 2 minutes (120s)
        start_lat += 0.0001
        start_lon += 0.0001
        
        iris_hub.connecter_machiniste(
            id_voiture="8358", 
            lat=start_lat, 
            lon=start_lon, 
            heading=180, 
            is_manoeuvre=False, 
            retard_sec=120
        )
        
        print(f"🕒 {datetime.datetime.now().strftime('%H:%M:%S')} - Position reçue : {start_lat}, {start_lon}")
        time.sleep(10) # Rafraîchissement toutes les 10 secondes
