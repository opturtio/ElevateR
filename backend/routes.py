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
        limit = int(data.get('limit', 120))
        limit = max(1, min(limit, 100))

        nearest_stations = elevate(lat, lon, stations, limit=limit, batch_size=6, max_workers=10)
        return jsonify(nearest_stations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
