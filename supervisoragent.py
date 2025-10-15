from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import requests, json

load_dotenv()

import json
import requests

@tool("search_flights_in_india")
def search_flights_in_india(params_json: str, min_results: int = 10) -> str:
    """
    Searches for flights between two locations in India, returning details with amounts in INR.
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

    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    headers = {
        "x-rapidapi-key": "ca1e8d5063msh497378f526e9313p1e7d37jsncd6865999253",
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
            "currency_code": "INR"
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
        "x-rapidapi-key": "ca1e8d5063msh497378f526e9313p1e7d37jsncd6865999253",
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

@tool("search_hotels_in_india")
def search_hotels_in_india(params_json: str, min_results: int = 10) -> str:
    """
    Searches for hotels in a given location in India using the Booking.com API.
    Continues fetching pages until at least `min_results` are gathered or no more pages exist.

    Args:
        params_json: JSON string containing parameters:
            - dest_id
            - search_type
            - arrival_date (yyyy-mm-dd)
            - departure_date (yyyy-mm-dd)
            - adults (default=1)
            - room_qty (default=1)
            - units (default='m')
            - temperature_unit (default='c')
            - languagecode (default='en-us')
            - currency_code (default='INR')
        min_results: Minimum number of results desired (default 10).

    Returns:
        JSON string containing a list of hotel details.
    """
    params = json.loads(params_json)

    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    headers = {
        "x-rapidapi-key": "ca1e8d5063msh497378f526e9313p1e7d37jsncd6865999253",
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    query = {
        "dest_id": params["dest_id"],
        "search_type": params["search_type"],
        "checkin_date": params["arrival_date"],
        "checkout_date": params["departure_date"],
        "adults": int(params.get("adults", 1)),
        "room_qty": int(params.get("room_qty", 1)),
        "units": params.get("units", "m"),
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
        
        if not data.get("data", {}).get("pagination", {}).get("next_page"):
            break  # no next page

        query["page_number"] += 1  # go to next page

    return json.dumps({"results": results[:min_results]})


model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

agent = create_react_agent(
    model= model,  
    tools=[search_flights_in_india],  
    prompt="You are an agent which gives details of 10 flights between source and destination from start date till retrun date."  
)

result=agent.invoke(
    {"messages": [{"role": "user", "content": "Source delhi, destibation bombay. Start date 25th Oct 2025, return date 30th October 2025"}]})

for message in result["messages"]:
    message.pretty_print()
