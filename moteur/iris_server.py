from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Crucial pour la liaison téléphone <-> serveur <-> ordinateur

# Stockage temporaire (en mémoire - se vide si le serveur redémarre)
bus_data = {}
pcc_orders = {}
performance_logs = []

@app.route('/update_position', methods=['POST'])
def update_position():
    data = request.get_json()
    pol = data.get('pol')
    if pol:
        bus_data[pol] = {
            "lat": data.get('lat'),
            "lon": data.get('lon'),
            "speed": data.get('speed'),
            "status": data.get('status'),
            "last_seen": datetime.now().strftime("%H:%M:%S")
        }
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "No POL provided"}), 400

@app.route('/get_buses', methods=['GET'])
def get_buses():
    # Cette route alimente la carte de ton PCC
    return jsonify(bus_data)

@app.route('/send_order', methods=['POST'])
def send_order():
    data = request.get_json()
    pol = data.get('pol')
    instruction = data.get('instruction')
    pcc_orders[pol] = instruction
    return jsonify({"status": "order_sent"}), 200

@app.route('/check_order/<pol>', methods=['GET'])
def check_order(pol):
    # Le téléphone du chauffeur interroge cette route toutes les 4s
    order = pcc_orders.get(pol, None)
    return jsonify({"order": order})

@app.route('/clear_order/<pol>', methods=['POST'])
def clear_order(pol):
    if pol in pcc_orders:
        del pcc_orders[pol]
    return jsonify({"status": "cleared"})

# --- NOUVEAU : SYSTÈME D'ARCHIVAGE DES PERFORMANCES ---

@app.route('/log_perf', methods=['POST'])
def log_perf():
    data = request.get_json()
    performance_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pol": data.get('pol'),
        "point": data.get('point'),
        "delay": data.get('delay')
    })
    # Garde les 500 derniers événements en mémoire
    if len(performance_logs) > 500:
        performance_logs.pop(0)
    return jsonify({"status": "logged"}), 200

@app.route('/get_logs', methods=['GET'])
def get_logs():
    # Route pour télécharger le CSV depuis le PCC
    return jsonify(performance_logs)

if __name__ == '__main__':
    # Sur PythonAnywhere, cette ligne ne sera pas utilisée par le serveur Web
    app.run(debug=True)
