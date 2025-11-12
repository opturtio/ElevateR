import requests
from app import stations
import os
from dotenv import load_dotenv
import math
import time

# Load environment variables from a .env file, which contains sensitive information such as API keys
load_dotenv()

# Define the URL for the HSL (Helsinki Region Transport) API
ROUTING_API_URL = 'https://api.digitransit.fi/routing/v2/hsl/gtfs/v1'

# Retrieve the API key from the environment variables loaded from the .env file
HSL_API_KEY = os.getenv('HSL_API_KEY')  # Ensure the API key is in the .env file

def send_query(query, timeout=45, retries=1, backoff=2.0):
    if not HSL_API_KEY:
        raise RuntimeError("Missing HSL_API_KEY in environment")
    headers = {
        'Content-Type': 'application/json',
        'digitransit-subscription-key': HSL_API_KEY
    }
    try:
        res = requests.post(ROUTING_API_URL, json={'query': query}, headers=headers, timeout=timeout)
        if res.status_code >= 500 or res.status_code in (429, 504):
            if retries > 0:
                time.sleep(backoff)
                return send_query(query, timeout=timeout, retries=retries - 1, backoff=backoff * 2)
        res.raise_for_status()
        payload = res.json()
        if 'errors' in payload:
            raise RuntimeError(str(payload['errors']))
        return payload
    except requests.RequestException as e:
        if retries > 0:
            time.sleep(backoff)
            return send_query(query, timeout=timeout, retries=retries - 1, backoff=backoff * 2)
        raise RuntimeError(f"Routing API request failed: {e}")

def elevate(origin_lat, origin_lon, stations, limit=60, batch_size=20):
    origin_lat = float(origin_lat)
    origin_lon = float(origin_lon)

    nearest_stations = get_nearest_stations(stations, origin_lat, origin_lon, limit=limit)

    results = []
    for start in range(0, len(nearest_stations), batch_size):
        chunk = nearest_stations[start:start + batch_size]
        parts = []
        for i, s in enumerate(chunk):
            parts.append(f"""
              p{i}: plan(
                from: {{ lat: {origin_lat}, lon: {origin_lon} }},
                to: {{ lat: {s['lat']}, lon: {s['lon']} }},
                numItineraries: 1,
                transportModes: [
                  {{mode: BUS}}, {{mode: TRAM}}, {{mode: SUBWAY}}, {{mode: RAIL}}, {{mode: FERRY}}, {{mode: WALK}}
                ]
              ) {{
                itineraries {{ duration }}
              }}
            """)
        query = f"query {{{''.join(parts)}}}"

        payload = send_query(query, timeout=45, retries=1)
        data = payload.get('data', {}) or {}

        for i, s in enumerate(chunk):
            plan = data.get(f"p{i}") or {}
            itins = plan.get('itineraries') or []
            if not itins:
                continue
            duration = itins[0].get('duration')
            if duration is None:
                continue
            results.append({
                'name': s['name'],
                'lat': s['lat'],
                'lon': s['lon'],
                'travel_time': duration
            })

        # Small delay between batches to be nice to the API
        time.sleep(0.2)

    return results

def get_nearest_stations(stations, origin_lat, origin_lon, limit=1000):
    items = []
    for s in stations:
        d = haversine(origin_lat, origin_lon, s['lat'], s['lon'])
        items.append({'name': s['name'], 'lat': s['lat'], 'lon': s['lon'], 'distance': d})
    items.sort(key=lambda x: x['distance'])
    return items[:limit]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c