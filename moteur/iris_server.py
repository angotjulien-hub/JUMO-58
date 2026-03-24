from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Autorise la communication avec le téléphone

# Stockage temporaire (en mémoire)
bus_data = {}
pcc_orders = {}

@app.route('/update_position', methods=['POST'])
def update_position():
    data = request.get_json()
    pol = data.get('pol')
    bus_data[pol] = {
        "lat": data.get('lat'),
        "lon": data.get('lon'),
        "speed": data.get('speed'),
        "status": data.get('status'),
        "last_seen": data.get('timestamp')
    }
    return jsonify({"status": "success"}), 200

@app.route('/get_buses', methods=['GET'])
def get_buses():
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
    order = pcc_orders.get(pol, None)
    return jsonify({"order": order})

@app.route('/clear_order/<pol>', methods=['POST'])
def clear_order(pol):
    if pol in pcc_orders:
        del pcc_orders[pol]
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    app.run(debug=True)
