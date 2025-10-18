
#langchain and langgraph libraries
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

#langsmith libraries for observability and monitoring
from langsmith import Client
from langsmith.run_helpers import traceable

#some other libraries
from dotenv import load_dotenv

load_dotenv()
client = Client()


from tools.search_flight_tool import search_flights
from tools.get_location_details_tool import get_location_details
from tools.search_hotels_tool import search_hotels
from tools.fetch_attraction_id_tool import fetch_attraction_location_id
from tools.search_tourist_attractions import search_tourist_attractions

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

### 1. Flight Agent
- Use this agent first.
- Fetch details of at least **20 available flights** for the given trip (source → destination → return if applicable).

### 2. Hotel Agent
- Use this agent second.
- Fetch details of at least **20 suitable hotels** in or near the destination.

### 3. Tourist Agent
- Use this agent last.
- Fetch details of at least **30 tourist attractions or activities** in the destination city.

---

### Your Objective
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

### Output Requirements
Return the final result as a **beautifully formatted travel summary in plain English**, not in JSON.

Structure it as follows:

---

**Flight Options Summary**
- Summarize the key flight options found (best economy and luxury).
- Mention airlines, departure/arrival times, and approximate prices.

**Hotel Options Summary**
- Brief overview of hotels found, including average prices and top-rated picks.

---

## Most Economical Package
1. **Flight:** [airline, flight number, class, price, duration] \n
2. **Hotel:** [hotel name, rating, price per night, total stay cost] \n  
3. **Attractions:** [list names with short descriptions]  \n
4. **Total Estimated Cost:** ₹_____ \n

---

## Most Luxurious Package
1. **Flight:** [airline, flight number, class, price, duration] \n  
2. **Hotel:** [hotel name, rating, amenities, total stay cost]  \n
3. **Attractions:** [list exclusive places or experiences]  \n
4. **Total Estimated Cost:** ₹_____ \n

---

### Final Summary
End with a short, friendly summary comparing both options, e.g.:

> “The Economical package offers excellent value for travelers on a budget, while the Luxurious option ensures a premium experience with top-tier comfort and attractions.”

---

### Rules
1. **Sequential Execution Only:** Call agents in this order → Flight → Hotel → Tourist.  
2. **One Call per Agent:** Use each only once unless the previous execution of agent did not yield desired result and hence needed a retry.  
3. **No Fabrication:** Use real data returned by agents.  
4. **Natural Language Output:** Final answer must be clear, well-formatted, and easily readable — **no JSON, no raw data dumps**.
"""
).compile()



# ------------------------------------------------
# Streamlit UI
# ------------------------------------------------

import app as st

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