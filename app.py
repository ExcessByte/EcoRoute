import json

from flask import Flask, jsonify, render_template
from flask_cors import CORS

from route_optimizer import RoadAwareOptimizer

app = Flask(__name__)
CORS(app)
optimizer = RoadAwareOptimizer()

DEPOT = {"lat": 10.374640, "lon": 76.307205, "name": "Collection Center"}

def load_bins_from_json():
    with open('bins.json', 'r') as f:
        return json.load(f)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/config')
def get_config():
    return jsonify({"depot": DEPOT})

@app.route('/api/bins', methods=['GET'])
def get_bins():
    return jsonify(load_bins_from_json())

@app.route('/api/optimize', methods=['POST'])
def run_optimization():
    bins = load_bins_from_json()
    routes = optimizer.optimize(bins)
    return jsonify({'routes': routes})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
