import json
import datetime
import os

class HubReceptionP2P:
    def __init__(self):
        # Tes fichiers cibles pour l'audit et l'affichage
        self.log_file = "referentiel/flux_live_2026.json"
        self.heatmap_file = "heatmap_coords.json"
        self.audit_file = "referentiel/audit_performance.csv"

    def connecter_machiniste(self, id_voiture, lat, lon, heading, is_manoeuvre, retard_sec=0):
        timestamp = datetime.datetime.now().isoformat()
        
        # Structure de donnée enrichie pour le SAEIV et l'IDFM
        donnee = {
            "timestamp": timestamp,
            "voiture": id_voiture,
            "lat": float(lat),
            "lon": float(lon),
            "cap": heading,
            "manoeuvre": is_manoeuvre,
            "retard_sec": retard_sec,
            "statut": "EN_MANOEUVRE" if is_manoeuvre else "EN_LIGNE"
        }
        
        # Logique de détection de couplage (Point fort IRIS)
        if retard_sec > 600 or is_manoeuvre:
            donnee["alerte"] = "⚠️ PRIORITÉ RÉGULATION - COUPLAGE DÉTECTÉ"
        
        self._sauvegarder_flux(donnee)
        self._generer_heatmap() 
        return donnee

    def _sauvegarder_flux(self, donnee):
        # 1. Sauvegarde dans le JSON pour le Live
        flux = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                try:
                    flux = json.load(f)
                except: flux = []
        
        flux.append(donnee)
        # On garde les 50 dernières positions pour ne pas alourdir le hub
        with open(self.log_file, "w") as f:
            json.dump(flux[-50:], f, indent=4)

        # 2. Sauvegarde dans le CSV pour l'audit final (Historisation)
        with open(self.audit_file, "a") as f:
            if os.stat(self.audit_file).st_size == 0:
                f.write("Date;Voiture;Lat;Lon;Cap;Manoeuvre;Retard\n")
            f.write(f"{donnee['timestamp']};{donnee['voiture']};{donnee['lat']};{donnee['lon']};{donnee['cap']};{donnee['manoeuvre']};{donnee['retard_sec']}\n")

    def _generer_heatmap(self):
        # Logique pour mettre à jour heatmap_coords.json utilisé par pcc_controle.html
        pass

# Instance pour le moteur de collecte
iris_hub = HubReceptionP2P()
