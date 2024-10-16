import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file, which contains sensitive information such as API keys
load_dotenv()

# Define the URL for the HSL (Helsinki Region Transport) API
HSL_API_URL = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'

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
    
    # Set the request headers, including the required API key for authentication
    headers = {
        'Content-Type': 'application/json',
        'digitransit-subscription-key': HSL_API_KEY  # Required API key header
    }

    # Send a POST request to the HSL API with the GraphQL query
    response = requests.post(HSL_API_URL, json={'query': query}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        valid_stations = [station for station in data['data']['stopsByBbox'] if station['vehicleType'] in [0, 1, 109, 3, 4]]
        return valid_stations
    else:
        raise Exception(f"Failed to fetch stations: {response.status_code}, {response.text}")

# Fetch Helsinki stations and handle any potential exceptions
try:
    helsinki_stations = fetch_helsinki_stations()
except Exception as e:
    print(e)
