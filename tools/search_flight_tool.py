from langchain.tools import tool
import requests, json
import os


@tool("search_flights")
def search_flights(params_json: str, min_results: int = 10) -> str:
    """
    Searches for flights between two locations, returning details with amounts in currency user has specified.
    If not enough results from page 1, continues fetching additional pages until min_results reached or no more pages.

    Args:
        params_json: JSON string with parameters:
            - from_id: Origin airport code (e.g., 'BOM.AIRPORT').
            - to_id: Destination airport code (e.g., 'DEL.AIRPORT').
            - depart_date: Departure date (YYYY-MM-DD).
            - return_date: Optional return date.
            - adults: Optional number of adults.
            - children: Optional children ages.
            - cabin_class: Optional cabin class ('ECONOMY', 'BUSINESS', etc.).
            - currency_code: 'INR', 'EUR', 'USD'. Default='INR'
        min_results: Minimum number of results desired (default 10).

    Returns:
        JSON string of accumulated flight search response items.
    """

    params = json.loads(params_json)
    from_id = params["from_id"]
    to_id = params["to_id"]
    depart_date = params["depart_date"]
    return_date = params.get("return_date", None)
    adults = int(params.get("adults", 1))
    children = params.get("children", "0")
    cabin_class = params.get("cabin_class", "ECONOMY")
    currency_code = params.get("currency_code", "INR")

    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }
    
    all_results = []
    page_no = 1
    
    while True:
        querystring = {
            "fromId": from_id,
            "toId": to_id,
            "departDate": depart_date,
            "returnDate": return_date,
            "stops": "none",
            "pageNo": str(page_no),
            "adults": str(adults),
            "children": children,
            "sort": "BEST",
            "cabinClass": cabin_class,
            "currency_code": currency_code
        }
        
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        response = response.json()

        # Assuming data contains a key "results" with list of flights
        flights = response.get("data", {}).get("flightOffers", [])

        all_results.extend(flights)


        # If enough results gathered or no more results, stop
        if len(all_results) >= min_results or not flights:
            break
        
        page_no += 1

    # Optionally trim to min_results if more than requested
    #all_results = all_results[:min_results]

    # Return JSON string of accumulated results
    return json.dumps({"results": all_results})
