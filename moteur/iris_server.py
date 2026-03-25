from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

# --- CONFIGURATION ---
base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(base_dir)
template_dir = os.path.join(root_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# Autorise GitHub et les autres domaines à interroger ton serveur
CORS(app, resources={r"/*": {"origins": "*"}})

# Base de données en temps réel
iris_db = {
    "buses": {},  
    "orders": {}  
}

@app.route('/')
def home():
    return render_template('pcc_controle.html')

# --- NOUVELLE ROUTE LOGIN ---
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Identifiants de test (à modifier selon tes besoins)
        if username == "admin" and password == "1234":
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Accès refusé"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/get_pcc_data')
def get_pcc_data():
    return jsonify(iris_db)

@app.route('/sync', methods=['POST'])
def sync():
    try:
        data = request.get_json()
        pol = str(data.get('pol', '5801'))

        iris_db["buses"][pol] = {
            "lat": float(data.get('lat')),
            "lon": float(data.get('lon')),
            "speed": data.get('speed', 0),
            "status": data.get('status', 'EN SERVICE'),
            "last_seen": datetime.now().strftime("%H:%M:%S")
        }

        order = iris_db["orders"].get(pol, None)
        
        return jsonify({
            "status": "success",
            "order": order
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/send_order', methods=['POST'])
def send_order():
    data = request.get_json()
    pol = data.get('pol')
    # Harmonisation : on accepte 'instruction' ou 'msg'
    instruction = data.get('instruction') or data.get('msg')
    
    if pol:
        iris_db["orders"][pol] = instruction
        return jsonify({"status": "sent"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/clear_order/<pol>', methods=['POST'])
def clear_order(pol):
    iris_db["orders"].pop(pol, None)
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
