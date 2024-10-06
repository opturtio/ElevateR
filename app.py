from os import getenv
from flask import Flask
from flask_cors import CORS
from backend.fetch_stations import fetch_helsinki_stations

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
app.secret_key = getenv("SECRET_KEY")
CORS(app)

# Fetch all the Helsinki stations when the app starts
stations = fetch_helsinki_stations()

from backend import routes  # noqa: E402, F401

if __name__ == "__main__":
    app.run(debug=True)
