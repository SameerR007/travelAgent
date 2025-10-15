from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
import os

os.environ["GOOGLE_API_KEY"]="AIzaSyDryKkzNwN6nvz97QWu6UAHbvtsd-aLWM8"

prompt = hub.pull("hwchase17/react")
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

search_tool = DuckDuckGoSearchRun()
import json
from langchain.tools import tool
import requests

@tool("search_flights_in_india")
def search_flights_in_india(params_json: str) -> str:
    """
    Searches for flights between two locations in India, returning details with amounts in INR.

    Args:
        params_json: JSON string containing parameters:
            - from_id: Origin airport code (e.g., 'BOM.AIRPORT').
            - to_id: Destination airport code (e.g., 'DEL.AIRPORT').
            - depart_date: Departure date ('YYYY-MM-DD').
            - return_date: Return date ('YYYY-MM-DD'), optional.
            - adults: Number of adults (integer), optional.
            - children: Comma-separated ages (string), optional.
            - cabin_class: 'ECONOMY', 'BUSINESS', etc., optional.

    Returns:
        Flight search results in INR.
    """
    params = json.loads(params_json)
    from_id = params["from_id"]
    to_id = params["to_id"]
    depart_date = params["depart_date"]
    return_date = params.get("return_date", None)
    adults = int(params.get("adults", 1))
    children = params.get("children", "0")
    cabin_class = params.get("cabin_class", "ECONOMY")

    print(f"Searching flights: from {from_id} to {to_id} on {depart_date} returning {return_date}, class {cabin_class}")

    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    querystring = {
        "fromId": from_id,
        "toId": to_id,
        "departDate": depart_date,
        "returnDate": return_date,
        "stops": "none",
        "pageNo": "1",
        "adults": str(adults),
        "children": children,
        "sort": "BEST",
        "cabinClass": cabin_class,
        "currency_code": "INR"  # Always INR for results
    }
    headers = {
        "x-rapidapi-key": "ca1e8d5063msh497378f526e9313p1e7d37jsncd6865999253",  # Use your valid key
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()
    return response.json()

tools= [search_flights_in_india]

agent = create_react_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

print(agent_executor.invoke({"input": "Find direct economy flights from Mumbai (BOM) to Delhi (DEL) departing on 2025-10-15 and returning 2025-10-30. Show prices in INR."}))