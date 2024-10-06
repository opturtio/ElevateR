from flask import render_template, jsonify, Response
from app import app, stations
from backend.elevate import elevate

@app.route("/")
def index():
    return render_template("index.html", stations=stations)

# Route to handle the elevation calculation
@app.route('/elevate', methods=['POST'])
def trigger_elevate():
    try:
        # Call the elevate function directly (no subprocess needed)
        elevate()
        return Response(status=204)  # 204 No Content: Request processed, no content to return
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
