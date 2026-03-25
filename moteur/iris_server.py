from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from datetime import datetime

# --- CONFIGURATION DES CHEMINS ---
base_dir = os.path.dirname(os.path.abspath(__file__))
# Remonte d'un niveau pour trouver le dossier 'templates' à la racine
root_dir = os.path.dirname(base_dir)
template_dir = os.path.join(root_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
CORS(app) # Autorise les connexions depuis GitHub et les mobiles

# --- BASES DE DONNÉES EN MÉMOIRE ---
bus_data = {}         # Positions en temps réel
pcc_orders = {}       # Ordres en attente pour les chauffeurs
performance_logs = [] # Historique des ponctualités

@app.route('/')
def home():
    """Affiche la console de contrôle (PCC)"""
    return render_template('pcc_controle.html')

@app.route('/health')
def health_check():
    """Vérification rapide du serveur"""
    return "IRIS SERVER V2.6 - OPERATIONNEL"

@app.route('/update_position', methods=['POST'])
def update_position():
    """REÇOIT les données des chauffeurs (chauffeur_pro_58.html)"""
    try:
        data = request.get_json()
        pol = str(data.get('pol'))
        
        if pol:
            bus_data[pol] = {
                "lat": data.get('lat'),
                "lon": data.get('lon'),
                "speed": data.get('speed', 0),
                "line": "58",
                "status": data.get('status', 'EN SERVICE'),
                "last_seen": datetime.now().strftime("%H:%M:%S")
            }
            return jsonify({"status": "success", "msg": "Position synchronisée"}), 200
        return jsonify({"status": "error", "msg": "POL manquant"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/get_buses', methods=['GET'])
def get_buses():
    """Envoie toutes les positions au PCC"""
    return jsonify(bus_data)

@app.route('/send_order', methods=['POST'])
def send_order():
    """Envoie un ordre depuis le PCC vers un chauffeur spécifique"""
    data = request.get_json()
    pol = data.get('pol')
    instruction = data.get('instruction')
    if pol and instruction:
        pcc_orders[pol] = instruction
        return jsonify({"status": "sent"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/check_order/<pol>', methods=['GET'])
def check_order(pol):
    """Le chauffeur vérifie s'il a un ordre en attente"""
    return jsonify({"order": pcc_orders.get(pol)})

@app.route('/clear_order/<pol>', methods=['POST'])
def clear_order(pol):
    """Efface l'ordre une fois que le chauffeur l'a lu"""
    pcc_orders.pop(pol, None)
    return jsonify({"status": "cleared"})

@app.route('/log_perf', methods=['POST'])
def log_perf():
    """Enregistre une donnée de performance (avance/retard)"""
    data = request.get_json()
    performance_logs.append(data)
    if len(performance_logs) > 500: 
        performance_logs.pop(0)
    return jsonify({"status": "logged"})

if __name__ == '__main__':
    # Utiliser le port 5000 par défaut pour les tests locaux
    app.run(debug=True, port=5000)
