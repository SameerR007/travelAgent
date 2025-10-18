from langchain.tools import tool
import requests
import os


@tool("get_location_details")
def get_location_details(city: str) -> dict:
    """
    Fetches location details (dest_id and search_type) for a given city 
    using the Booking.com API.

    Args:
        city (str): Name of the city to search for (e.g., "Paris", "New York").

    Returns:
        dict: Dictionary containing location details, for example:
              {
                 "dest_id": "-1456928",
                 "dest_type": "city",
                 "name": "Paris"
              }
    """

    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
    querystring = {"query": city}
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()

    data = response.json()["data"][0]
    return {
        "dest_id": data["dest_id"],
        "dest_type": data["dest_type"],
        "name": data["name"]
    }
