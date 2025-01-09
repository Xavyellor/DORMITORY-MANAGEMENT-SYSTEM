import requests

def geocode(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    headers = {
        "User-Agent": "YourAppName/1.0 (your-email@example.com)"
    }

    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return {
                "latitude": data[0]["lat"],
                "longitude": data[0]["lon"],
                "address": data[0]["display_name"]
            }
        else:
            return "No results found"
    else:
        return f"Error: {response.status_code}"
