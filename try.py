import requests

url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"

querystring = {"fromId":"BOM.AIRPORT","toId":"DEL.AIRPORT","stops":"none","pageNo":"1","adults":"1","children":"0,17","sort":"BEST","cabinClass":"ECONOMY","currency_code":"AED"}

headers = {
	"x-rapidapi-key": "ca1e8d5063msh497378f526e9313p1e7d37jsncd6865999253",
	"x-rapidapi-host": "booking-com15.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())