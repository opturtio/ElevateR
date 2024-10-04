import requests
import os
from dotenv import load_dotenv

load_dotenv()

HSL_API_URL = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
HSL_API_KEY = os.getenv('HSL_API_KEY')  # Fetch the API key from the .env file

def fetch_stations():
    query = """
    {
      stops {
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
        'Authorization': f'Bearer {HSL_API_KEY}'  # Pass the API key in the header
    }

    response = requests.post(HSL_API_URL, json={'query': query}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['stops']
    else:
        raise Exception(f"Failed to fetch stations: {response.status_code}, {response.text}")
