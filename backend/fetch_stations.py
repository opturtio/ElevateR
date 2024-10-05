import requests
import os
from dotenv import load_dotenv

# Load the .env file which contains your API key
load_dotenv()

HSL_API_URL = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
HSL_API_KEY = os.getenv('HSL_API_KEY')  # Ensure the API key is in the .env file

def fetch_helsinki_stations():
    # GraphQL query to fetch stops within the bounding box of Helsinki
    query = """
    {
      stopsByBbox(minLat: 60.1, minLon: 24.7, maxLat: 60.3, maxLon: 25.19) {
        gtfsId
        name
        lat
        lon
        vehicleType
      }
    }
    """

    headers = {
        'Content-Type': 'application/json',
        'digitransit-subscription-key': HSL_API_KEY  # Required API key header
    }

    response = requests.post(HSL_API_URL, json={'query': query}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        valid_stations = [station for station in data['data']['stopsByBbox'] if station['vehicleType'] != -999]
        return valid_stations
    else:
        raise Exception(f"Failed to fetch stations: {response.status_code}, {response.text}")

# Fetch Helsinki stations
try:
    helsinki_stations = fetch_helsinki_stations()
    print(helsinki_stations)
except Exception as e:
    print(e)
