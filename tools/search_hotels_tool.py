from langchain.tools import tool
import requests, json
import os


@tool("search_hotels")
def search_hotels(params_json: str, min_results: int = 10) -> str:
    """
    Searches for hotels in a given location using the Booking.com API.
    Continues fetching pages until at least `min_results` are gathered or no more pages exist.

    Args:
        params_json: JSON string containing parameters:
            - dest_id
            - search_type
            - arrival_date (yyyy-mm-dd)
            - departure_date (yyyy-mm-dd)
            - adults (default=1)
            - room_qty (default=1)
            - units (default='metric')
            - temperature_unit (default='c')
            - languagecode: 'en-us', 'de', 'hi'. Default='en-us'
            - currency_code: 'INR', 'EUR', 'USD'. Default='INR'
        min_results: Minimum number of results desired (default 10).

    Returns:
        JSON string containing a list of hotel details.
    """
    params = json.loads(params_json)

    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    query = {
        "dest_id": params["dest_id"],
        "search_type": params["search_type"],
        "arrival_date": params["arrival_date"],
        "departure_date": params["departure_date"],
        "adults": int(params.get("adults", 1)),
        "room_qty": int(params.get("room_qty", 1)),
        "units": params.get("units", "metric"),
        "temperature_unit": params.get("temperature_unit", "c"),
        "languagecode": params.get("languagecode", "en-us"),
        "currency_code": params.get("currency_code", "INR"),
        "page_number": 1
    }

    results = []
    while len(results) < min_results:
        response = requests.get(url, headers=headers, params=query)
        response.raise_for_status()
        data = response.json()

        hotels = data.get("data", {}).get("hotels", [])
        if not hotels:
            break  # no more pages
        
        results.extend(hotels)
        

        query["page_number"] += 1  # go to next page

    return json.dumps({"results": results})
