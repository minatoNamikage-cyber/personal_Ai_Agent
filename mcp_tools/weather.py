import requests
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Weather Server")


HEADERS = {
    "User-Agent": "Eran-AI/1.0"
}


@mcp.tool()
def weather(city: str):
    """Get current weather information for a city."""

    geo = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": city,
            "format": "json",
            "limit": 1
        },
        headers=HEADERS,
        timeout=20
    ).json()

    if not geo:
        return {
            "error": "City not found"
        }

    lat = geo[0]["lat"]
    lon = geo[0]["lon"]

    weather_data = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
        },
        timeout=20
    ).json()

    weather = weather_data["current"]

    return {
        "City": city.title(),
        "Temperature": f'{weather["temperature_2m"]} °C',
        "Humidity": f'{weather["relative_humidity_2m"]} %',
        "Wind Speed": f'{weather["wind_speed_10m"]} km/h'
    }


if __name__ == "__main__":
    mcp.run()