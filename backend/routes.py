from flask import render_template, jsonify, request
from app import app, stations
from backend.elevate import elevate

@app.route("/")
def index():
    return render_template("index.html", stations=stations)

# Route to handle the elevation calculation
@app.route('/elevate', methods=['POST'])
def trigger_elevate():
    try:
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')

        nearest_stations = elevate(lat, lon)
        return jsonify(nearest_stations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
