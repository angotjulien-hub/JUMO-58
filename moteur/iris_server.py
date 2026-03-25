from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os

# --- CONFIGURATION DES CHEMINS ---
base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(base_dir)
# Flask cherchera le HTML dans /home/angot/angotjulien-hub/templates/
template_dir = os.path.join(root_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
CORS(app) # Autorise la connexion depuis ton GitHub JUMO-58

# Base de données en temps réel (Mémoire vive)
iris_db = {
    "buses": {},  # Stockage des POL (ex: 5801)
    "orders": {}  # Ordres envoyés aux chauffeurs
}

@app.route('/')
def home():
    """Affiche la carte de contrôle (PCC)"""
    return render_template('pcc_controle.html')

@app.route('/get_pcc_data')
def get_pcc_data():
    """Envoie les positions au format JSON au PCC"""
    return jsonify(iris_db)

@app.route('/sync', methods=['POST'])
def sync():
    """REÇOIT les données du fichier chauffeur_pro_58.html"""
    try:
        data = request.get_json()
        pol = str(data.get('pol', '5800'))
        
        # Mise à jour de la base de données
        iris_db["buses"][pol] = {
            "lat": float(data.get('lat')),
            "lon": float(data.get('lon')),
            "status": data.get('status', 'EN LIGNE'),
            "speed": data.get('speed', 0),
            "line": "58"
        }
        return jsonify({"status": "ok", "msg": "Position synchronisée"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
