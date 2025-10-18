from langchain.tools import tool
import requests, json
import os


@tool("search_tourist_attractions")
def search_tourist_attractions(params_json: str, min_results: int = 30) -> str:
    """
    Searches for tourist attractions in a given location using the Booking.com API.
    Continues fetching pages until at least `min_results` are gathered or no more pages exist.

    Args:
        params_json: JSON string containing parameters:
            - id : can be retrieved from fetch_attraction_location_id tool
            - languagecode: 'en-us', 'de', 'hi'. Default='en-us'
            - currency_code: 'INR', 'EUR', 'USD'. Default='INR'
        min_results: Minimum number of results desired (default 30).

    Returns:
        JSON string containing a list of tourist attraction details.
    """
    params = json.loads(params_json)

    url = "https://booking-com15.p.rapidapi.com/api/v1/attraction/searchAttractions"
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    query = {
        "id": params["id"],
        "sortBy": "trending",
        "languagecode": params.get("languagecode", "en-us"),
        "currency_code": params.get("currency_code", "INR"),
        "page_number": 1
    }

    results = []
    while len(results) < min_results:
        response = requests.get(url, headers=headers, params=query)
        response.raise_for_status()
        data = response.json()

        tourist_sites = data.get("data", {}).get("products", [])
        if not tourist_sites:
            break  # no more pages
        
        results.extend(tourist_sites)
        

        query["page_number"] += 1  # go to next page

    return json.dumps({"results": results})
