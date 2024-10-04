from os import getenv
from flask import Flask
from flask_cors import CORS
from backend.fetch_stations import fetch_stations

app = Flask(__name__, template_folder="frontend/templates")
app.secret_key = getenv("SECRET_KEY")
CORS(app)

# Fetch all the Helsinki stations when the app starts
stations = fetch_stations()

from backend import routes

if __name__ == "__main__":
    app.run(debug=True)
