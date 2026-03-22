from flask import Flask, jsonify, request
from flask_cors import CORS # Obligatoire pour le Web

app = Flask(__name__)
CORS(app) # Autorise tes pages GitHub à lire les données

bus_positions = {}

@app.route('/update_position', methods=['POST'])
def update():
    data = request.get_json()
    pol = data.get('pol')
    bus_positions[pol] = {
        "id": pol,
        "lat": data.get('lat'),
        "lng": data.get('lon'),
        "eid": data.get('eid', 0)
    }
    return jsonify({"status": "success"})

@app.route('/get_stats', methods=['GET'])
def stats():
    return jsonify({"bus_positions": list(bus_positions.values())})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) # Écoute sur tout le réseau
