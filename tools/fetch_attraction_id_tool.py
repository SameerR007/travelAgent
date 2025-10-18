from langchain.tools import tool
import requests, json
import os


@tool("fetch_attraction_location_id")
def fetch_attraction_location_id(params_json: str) -> dict:
    """
    Fetches search_attraction_location_id (id) for a given city 
    using the Booking.com API.

    Args:
        params_json: JSON string containing parameters:
            - city (str): Name of the city to search for (e.g., "Paris", "New York").
            - languagecode: 'en-us', 'de', 'hi'. Default='en-us'
    Returns:
        dict: Dictionary containing location details, for example:
              {
                "id": "eyJwaW5uZWRQcm9kdWN0IjoiUFJKN2RIa0FlWllaIiwidWZpIjoyMDA4ODMyNX0=",
              }
    """

    params = json.loads(params_json)


    url = "https://booking-com15.p.rapidapi.com/api/v1/attraction/searchLocation"
    querystring = {"query": params["city"], "languagecode": params.get("languagecode", "en-us")}
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()

    data = response.json()["data"]["products"][0]
    return {
        "id": data["id"],
        "name": data["cityName"]
    }
