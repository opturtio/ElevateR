import requests
from app import stations
import os
from dotenv import load_dotenv
import math

# Load environment variables from a .env file, which contains sensitive information such as API keys
load_dotenv()

# Define the URL for the HSL (Helsinki Region Transport) API
HSL_API_URL = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'

# Retrieve the API key from the environment variables loaded from the .env file
HSL_API_KEY = os.getenv('HSL_API_KEY')  # Ensure the API key is in the .env file

def send_query(query):
    headers = {
        'Content-Type': 'application/json',
        'digitransit-subscription-key': HSL_API_KEY
    }
    response = requests.post(HSL_API_URL, json={'query': query}, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

def elevate():
    queries = []  # List to store the queries
    origin_lat = 60.1699  # Latitude of the origin station (Helsinki Central Station)
    origin_lon = 24.9384  # Longitude of the origin station

    # Get the 100 nearest stations
    nearest_stations = get_nearest_stations(stations, origin_lat, origin_lon, limit=100)

    # Build a single GraphQL query for the 100 nearest stations
    query_parts = []
    for i, station in enumerate(nearest_stations):
        query_parts.append(f"""
        itinerary{i}: plan(
            from: {{lat: {origin_lat}, lon: {origin_lon}}},
            to: {{lat: {station['lat']}, lon: {station['lon']}}},
            numItineraries: 1
        ) {{
            itineraries {{
                duration
                legs {{
                    mode
                    startTime
                    endTime
                    realTime
                    from {{
                        name
                    }}
                    to {{
                        name
                    }}
                }}
            }}
        }}
        """)

    # Combine the queries into a single request
    query = f"{{ {''.join(query_parts)} }}"

    try:
        # Send the batch query and get the response
        response = send_query(query)
        for i, station in enumerate(nearest_stations):
            itinerary_data = response['data'].get(f'itinerary{i}', {})
            travel_time = itinerary_data['itineraries'][0]['duration'] if itinerary_data.get('itineraries') else None
            if travel_time is not None:
                queries.append({
                    'station_name': station['name'],
                    'travel_time': travel_time
                })
                print(f"Travel time to {station['name']}: {travel_time / 60:.2f} minutes")
            else:
                print(f"No itinerary found for {station['name']}")

    except Exception as e:
        print(f"Error querying stations: {str(e)}")

    print(f"Queries result: {queries}")
    return queries

def get_nearest_stations(stations, origin_lat, origin_lon, limit=100):
    """
    Sort stations by their distance from the origin and return the closest stations.
    Inputs: list of stations, origin latitude, origin longitude, limit (number of nearest stations to return)
    """
    stations_with_distance = []
    
    # Calculate distance for each station
    for station in stations:
        distance = haversine(origin_lat, origin_lon, station['lat'], station['lon'])
        stations_with_distance.append({
            'name': station['name'],
            'lat': station['lat'],
            'lon': station['lon'],
            'vehicleType': station['vehicleType'],
            'distance': distance
        })
    
    # Sort stations by distance
    stations_with_distance.sort(key=lambda x: x['distance'])
    
    # Return the nearest stations, limited by the given number
    return stations_with_distance[:limit]


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface.
    Inputs are latitude and longitude in decimal degrees.
    Returns distance in kilometers.
    """
    R = 6371.0  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
