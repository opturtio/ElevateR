from os import getenv
from flask import Flask
from flask_cors import CORS
from backend.fetch_stations import fetch_helsinki_stations

app = Flask(__name__, template_folder="frontend/templates")
app.secret_key = getenv("SECRET_KEY")
CORS(app)

# Fetch all the Helsinki stations when the app starts
stations = fetch_helsinki_stations()

vehicle_types = {
    0: 'Tram',
    1: 'Metro',
    2: 'Train',
    3: 'Bus',
    4: 'Ferry',
    5: 'Cable Car',
    6: 'Gondola/Chair Lift',
    7: 'Funicular',
    12: 'City Bike'
}

from backend import routes

if __name__ == "__main__":
    app.run(debug=True)
