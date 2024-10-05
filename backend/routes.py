from flask import render_template
from app import app, stations, vehicle_types

@app.route("/")
def index():
    return render_template("index.html", stations=stations, vehicle_types=vehicle_types)
