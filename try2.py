import requests

url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"

# Use the details returned from get_location_details("Mumbai")
querystring = {
    "dest_id": "-2106102",          # from get_location_details
    "search_type": "city",          # or "CITY" (case-insensitive)
    "arrival_date": "2025-10-20",   # required
    "departure_date": "2025-10-25",  # required
    "adults": "2",                  # number of adults
    "room_qty": "1",                # number of rooms
    "units": "metric",
    "temperature_unit": "c",
    "languagecode": "en-us",
    "currency_code": "INR",         # use INR for India
    "page_number": "1"
}

headers = {
    "x-rapidapi-key": "ca1e8d5063msh497378f526e9313p1e7d37jsncd6865999253",
    "x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
response.raise_for_status()

data = response.json()

print("Full API Response:")
print(data)

# Extract hotel details from the first few results
hotels = data.get("data", {}).get("hotels", [])
for i, hotel in enumerate(hotels[:5], start=1):
    print(f"\nHotel {i}:")
    print(f"Name: {hotel.get('property', {}).get('name')}")
    print(f"Price: {hotel.get('price_breakdown', {}).get('gross_price')}")
    print(f"Currency: {hotel.get('price_breakdown', {}).get('currency')}")
