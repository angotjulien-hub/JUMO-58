import csv
import json
import os

def run_parser():
    MOTEUR_DIR = "moteur"
    # Mapping des fichiers sources dans ton dossier moteur
    files_map = {
        "Semaine": "058_058LAV10_Semaine_01_SRIG2025_TR_Exp_20250311_151448.xlsx - TableauRegulation.csv",
        "Samedi": "058_058SAM30_Samedi_06_SRIG2025_TR_Exp_20250311_151448.xlsx - TableauRegulation.csv",
        "Dimanche": "058_058DIM10_Dimanche_04_SRIG2025_TR_Exp_20250311_151448.xlsx - TableauRegulation.csv"
    }

    master_data = {}

    for day_type, filename in files_map.items():
        path = os.path.join(MOTEUR_DIR, filename)
        if not os.path.exists(path):
            print(f"⚠️ Fichier absent : {filename}")
            continue

        day_db = {}
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            # Lecture à partir de la ligne 14 (index 13)
            for i in range(13, len(rows)):
                row = rows[i]
                if len(row) < 30 or not row[0].isdigit(): continue

                # Aller (Colonnes RATP standard)
                day_db[row[0]] = {
                    "dir": "Aller", "agent": row[3],
                    "stops": {"CTL": row[6], "LUX": row[8], "18J": row[9], "VM": row[12]}
                }
                # Retour
                if row[17] and row[17].isdigit():
                    day_db[row[17]] = {
                        "dir": "Retour", "agent": row[19],
                        "stops": {"VM": row[21], "18J": row[25], "LUX": row[26], "CTL": row[29]}
                    }
        master_data[day_type] = day_db

    with open('iris_master_data.json', 'w', encoding='utf-8') as f:
        json.dump(master_data, f, indent=4, ensure_ascii=False)
    print("✅ Base de données IRIS synchronisée.")

if __name__ == "__main__":
    run_parser()
