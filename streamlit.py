from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import requests, json

load_dotenv()

import json
import requests

from langsmith import Client
from langsmith.run_helpers import traceable


client = Client()


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
        "x-rapidapi-key": "ca1e8d5063msh497378f526e9313p1e7d37jsncd6865999253",
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
        "x-rapidapi-key": "ca1e8d5063msh497378f526e9313p1e7d37jsncd6865999253",
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()

    data = response.json()["data"]["products"][0]
    return {
        "id": data["id"],
        "name": data["cityName"]
    }


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
        "x-rapidapi-key": "ca1e8d5063msh497378f526e9313p1e7d37jsncd6865999253",
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



model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

flight_agent = create_react_agent(
    model= model,  
    tools=[search_flights],  
    prompt="You are an agent which gives details of 20 flights between source and destination from start date till return date.",  
	name="flight_agent"
)

hotel_agent = create_react_agent(
    model= model,  
    tools=[search_hotels, get_location_details],  
    prompt="You are an agent which gives detailed hotel details of 20 hotels in a given location.",
    name="hotel_agent"
    
)

tourist_agent = create_react_agent(
    model= model,  
    tools=[search_tourist_attractions, fetch_attraction_location_id],  
    prompt="You are an agent which gives detailed details of 30 places to visit in a given location.",
    name="tourist_agent"
)


from langgraph_supervisor import create_supervisor

supervisor = create_supervisor(
    model=model,
    agents=[flight_agent, hotel_agent, tourist_agent],
    output_mode="last_message",
    prompt="""
You are a **Trip Planning Supervisor Agent** responsible for creating complete travel itineraries for users.

You will receive the following inputs from the user:
- Source city/airport  
- Destination city/airport  
- Trip start date (departure)  
- Trip return date (if applicable)

Your job is to use your three sub-agents to design a personalized travel plan:

### 🛫 1. Flight Agent
- Use this agent first.
- Fetch details of at least **20 available flights** for the given trip (source → destination → return if applicable).

### 🏨 2. Hotel Agent
- Use this agent second.
- Fetch details of at least **20 suitable hotels** in or near the destination.

### 🎡 3. Tourist Agent
- Use this agent last.
- Fetch details of at least **30 tourist attractions or activities** in the destination city.

---

### 🎯 Your Objective
After gathering the results from all agents **(in the above sequence)**, analyze them to produce **two distinct travel packages**:

#### (A) The Most Economical Package
- Choose the **lowest total cost** combination of flight + hotel.
- Include some (depending on the number of vacation days) of nearby attractions that are **budget-friendly** or free to visit.

#### (B) The Most Luxurious Package
- Choose the **most premium experience**, combining:
  - A business-class or top-rated flight.
  - A highly rated luxury hotel.
  - Include some (depending on the number of vacation days) exclusive or must-visit attractions.

---

### 🧾 Output Requirements
Return the final result as a **beautifully formatted travel summary in plain English**, not in JSON.

Structure it as follows:

---

**✈️ Flight Options Summary**
- Summarize the key flight options found (best economy and luxury).
- Mention airlines, departure/arrival times, and approximate prices.

**🏨 Hotel Options Summary**
- Brief overview of hotels found, including average prices and top-rated picks.

---

## 🪙 Most Economical Package
1. **Flight:** [airline, flight number, class, price, duration] \n
2. **Hotel:** [hotel name, rating, price per night, total stay cost] \n  
3. **Attractions:** [list names with short descriptions]  \n
4. **💰 Total Estimated Cost:** ₹_____ \n

---

## 💎 Most Luxurious Package
1. **Flight:** [airline, flight number, class, price, duration] \n  
2. **Hotel:** [hotel name, rating, amenities, total stay cost]  \n
3. **Attractions:** [list exclusive places or experiences]  \n
4. **💵 Total Estimated Cost:** ₹_____ \n

---

### 🗒️ Final Summary
End with a short, friendly summary comparing both options, e.g.:

> “The Economical package offers excellent value for travelers on a budget, while the Luxurious option ensures a premium experience with top-tier comfort and attractions.”

---

### 🧩 Rules
1. **Sequential Execution Only:** Call agents in this order → Flight → Hotel → Tourist.  
2. **One Call per Agent:** Use each only once unless the previous execution of agent did not yield desired result and hence needed a retry.  
3. **No Fabrication:** Use real data returned by agents.  
4. **Natural Language Output:** Final answer must be clear, well-formatted, and easily readable — **no JSON, no raw data dumps**.
"""
).compile()



# ------------------------------------------------
# Streamlit UI
# ------------------------------------------------

import streamlit as st

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="centered")
st.title("🌍 AI Travel Planner")
st.write("Plan your trip with real data from Booking.com APIs — flights, hotels, and attractions!")

st.sidebar.header("🧳 Trip Details")
source = st.sidebar.text_input("Source City / Airport", "Delhi")
destination = st.sidebar.text_input("Destination City / Airport", "Munich")
depart_date = st.sidebar.date_input("Departure Date")
return_date = st.sidebar.date_input("Return Date")

currency = st.sidebar.selectbox("Currency", ["INR", "EUR", "USD"])

if st.sidebar.button("Plan My Trip 🚀"):
    with st.spinner("Planning your itinerary... This may take a minute ⏳"):

        user_query = (
            f"Source - {source}, Destination - {destination}. "
            f"Departure - {depart_date}, Arrival - {return_date}."
            f"Use currency: {currency} for api parameters."
        )

        @traceable(name="travelAgent_Supervisor_Run")
        def run_query():
            result = supervisor.invoke({"messages": [{"role": "user", "content": user_query}]})
            return result

        try:
            result = run_query()
            st.success("✅ Trip plan generated successfully!")
            print(result["messages"][-1].content)
            st.markdown(result["messages"][-1].content)
        except Exception as e:
            st.error(f"❌ Error: {e}")