import csv
import json
import os

def run_parser():
    # Configuration des chemins vers le dossier moteur
    MOTEUR_DIR = "moteur"
    
    # Mapping précis de tes fichiers de régulation
    files_map = {
        "Semaine": "058_058LAV10_Semaine_01_SRIG2025_TR_Exp_20250311_151448.xlsx - TableauRegulation.csv",
        "Samedi": "058_058SAM30_Samedi_06_SRIG2025_TR_Exp_20250311_151448.xlsx - TableauRegulation.csv",
        "Dimanche": "058_058DIM10_Dimanche_04_SRIG2025_TR_Exp_20250311_151448.xlsx - TableauRegulation.csv"
    }

    master_data = {}

    for day_type, filename in files_map.items():
        path = os.path.join(MOTEUR_DIR, filename)
        if not os.path.exists(path):
            print(f"❌ Erreur : {filename} introuvable dans /moteur")
            continue

        print(f"🛰️ IRIS Parsing : {day_type}...")
        day_db = {}

        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Début des données (généralement ligne 14)
            for i in range(13, len(rows)):
                row = rows[i]
                if len(row) < 30 or not row[0].isdigit(): continue

                # Extraction ALLER (Vers VM)
                tv_a = row[0]
                day_db[tv_a] = {
                    "dir": "Aller",
                    "stops": {"CTL": row[6], "LUX": row[8], "18J": row[9], "VM": row[12]}
                }

                # Extraction RETOUR (Vers CTL)
                tv_r = row[17]
                if tv_r and tv_r.isdigit():
                    day_db[tv_r] = {
                        "dir": "Retour",
                        "stops": {"VM": row[21], "18J": row[25], "LUX": row[26], "CTL": row[29]}
                    }
        
        master_data[day_type] = day_db

    with open('iris_master_data.json', 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=4)
    
    print("\n✅ Base IRIS générée : iris_master_data.json")

if __name__ == "__main__":
    run_parser()
