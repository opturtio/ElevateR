import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file, which contains sensitive information such as API keys
load_dotenv()

# Define the URL for the HSL (Helsinki Region Transport) API
HSL_API_URL = 'https://api.digitransit.fi/routing/v2/hsl/gtfs/v1'

# Retrieve the API key from the environment variables loaded from the .env file
HSL_API_KEY = os.getenv('HSL_API_KEY')  # Ensure the API key is in the .env file

def fetch_helsinki_stations():
    """
    Fetches public transport stations within a specific bounding box (latitude/longitude range) around Helsinki
    using a GraphQL query to the HSL API.

    Returns:
        list: A list of valid station data, including GTFS ID, name, latitude, longitude, and vehicle type.

    Raises:
        Exception: If the API request fails or returns a non-200 HTTP status code.
    """
    if not HSL_API_KEY:
      raise RuntimeError("Missing HSL_API_KEY in environment")

    
    # GraphQL query to fetch stops within the bounding box of Helsinki
    query = """
    {
      stopsByBbox(minLat: 60.1, minLon: 24.6, maxLat: 60.34, maxLon: 25.19) {
        gtfsId
        name
        lat
        lon
        vehicleMode
      }
    }
    """

    vehicle_modes = [
      'TRAM',
      'SUBWAY',
      'RAIL',
      'BUS',
      'FERRY'
    ]

    # Set the request headers, including the required API key for authentication
    headers = {
        'Content-Type': 'application/json',
        'digitransit-subscription-key': HSL_API_KEY  # Required API key header
    }

    # Send a POST request to the HSL API with the GraphQL query
    res = requests.post(HSL_API_URL, json={'query': query}, headers=headers, timeout=30)
    res.raise_for_status()
    payload = res.json()
    if 'errors' in payload:
        raise RuntimeError(str(payload['errors']))

    stops = payload.get('data', {}).get('stopsByBbox', []) or []

    # Map enum to your numeric vehicleType
    mode_to_type = {
        'TRAM': 0,
        'SUBWAY': 1,
        'RAIL': 109,
        'BUS': 3,
        'FERRY': 4
    }

    valid_stations = [
        {
            'gtfsId': s.get('gtfsId'),
            'name': s.get('name'),
            'lat': s.get('lat'),
            'lon': s.get('lon'),
            'vehicleMode': s.get('vehicleMode'),
            'vehicleType': mode_to_type.get(s.get('vehicleMode'))
        }
        for s in stops
        if s.get('vehicleMode') in mode_to_type
    ]
    return valid_stations

# Fetch Helsinki stations and handle any potential exceptions
try:
    helsinki_stations = fetch_helsinki_stations()
except Exception as e:
    print(e)
