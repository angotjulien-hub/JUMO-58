from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

# --- CONFIGURATION ---
base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(base_dir)
template_dir = os.path.join(root_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
CORS(app)

# Base de données en temps réel (Mémoire vive)
iris_db = {
    "buses": {},  # Stockage des positions et statuts
    "orders": {}  # Ordres envoyés aux chauffeurs
}

@app.route('/')
def home():
    """Affiche la console de contrôle"""
    return render_template('pcc_controle.html')

@app.route('/get_pcc_data')
def get_pcc_data():
    """Envoie toute la base de données au format JSON au PCC"""
    return jsonify(iris_db)

@app.route('/sync', methods=['POST'])
def sync():
    """REÇOIT les données du chauffeur et ENVOIE les ordres en retour (Boucle unique)"""
    try:
        data = request.get_json()
        pol = str(data.get('pol', '5801'))

        # 1. Mise à jour de la position du bus
        iris_db["buses"][pol] = {
            "lat": float(data.get('lat')),
            "lon": float(data.get('lon')),
            "speed": data.get('speed', 0),
            "status": data.get('status', 'EN SERVICE'),
            "last_seen": datetime.now().strftime("%H:%M:%S")
        }

        # 2. Vérification s'il y a un ordre pour ce bus
        order = iris_db["orders"].get(pol, None)
        
        return jsonify({
            "status": "success",
            "order": order
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/send_order', methods=['POST'])
def send_order():
    """Le PCC envoie un ordre ici"""
    data = request.get_json()
    pol = data.get('pol')
    instruction = data.get('instruction')
    if pol:
        iris_db["orders"][pol] = instruction
        return jsonify({"status": "sent"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/clear_order/<pol>', methods=['POST'])
def clear_order(pol):
    """Le chauffeur confirme avoir lu l'ordre"""
    iris_db["orders"].pop(pol, None)
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
