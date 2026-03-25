from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Bases de données en mémoire
bus_data = {}
pcc_orders = {}
performance_logs = []

@app.route('/')
def health_check():
    return "IRIS SERVER V2.6 - OPERATIONNEL"

@app.route('/update_position', methods=['POST'])
def update_position():
    data = request.get_json()
    pol = data.get('pol')
    if pol:
        bus_data[pol] = {
            "lat": data.get('lat'),
            "lon": data.get('lon'),
            "speed": data.get('speed', 0),
            "status": data.get('status', 'EN SERVICE'),
            "last_seen": datetime.now().strftime("%H:%M:%S")
        }
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/get_buses', methods=['GET'])
def get_buses():
    return jsonify(bus_data)

@app.route('/send_order', methods=['POST'])
def send_order():
    data = request.get_json()
    pol = data.get('pol')
    instruction = data.get('instruction')
    pcc_orders[pol] = instruction
    return jsonify({"status": "sent"}), 200

@app.route('/check_order/<pol>', methods=['GET'])
def check_order(pol):
    return jsonify({"order": pcc_orders.get(pol)})

@app.route('/clear_order/<pol>', methods=['POST'])
def clear_order(pol):
    pcc_orders.pop(pol, None)
    return jsonify({"status": "cleared"})

@app.route('/log_perf', methods=['POST'])
def log_perf():
    data = request.get_json()
    performance_logs.append(data)
    if len(performance_logs) > 500: performance_logs.pop(0)
    return jsonify({"status": "logged"})

if __name__ == '__main__':
    app.run(debug=True)
