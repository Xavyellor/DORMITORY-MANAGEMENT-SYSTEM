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

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP issues

        data = response.json()

        if data and isinstance(data, list) and len(data) > 0:
            print(f"DEBUG: Geocode API Response: {data[0]}")
            return {
                "latitude": data[0]["lat"],
                "longitude": data[0]["lon"],
                "address": data[0]["display_name"]
            }
        else:
            print(f"DEBUG: No geocode results found for {address}")
            return None

    except requests.RequestException as e:
        print(f"DEBUG: Geocode API Request Failed - {e}")
        return None
