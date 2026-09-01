"""
skills/weather.py -- Fetches live weather from an OpenWeatherMap-compatible
REST API using the free tier. The API key is read from the environment
(never hardcoded). If the key is missing or the request fails, this
degrades gracefully with a clear, spoken explanation instead of crashing.
"""

import requests
from config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL, DEFAULT_CITY, weather_configured


def get_weather(city: str = None) -> str:
    city = (city or DEFAULT_CITY).strip()

    if not weather_configured():
        return (
            "Live weather isn't available right now because no OpenWeatherMap API "
            "key is configured. Please add OPENWEATHER_API_KEY to your .env file. "
            f"(You asked about {city}.)"
        )

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=8)
    except requests.exceptions.RequestException as exc:
        return f"I couldn't reach the weather service right now. ({exc})"

    if response.status_code == 401:
        return "The weather API key appears to be invalid. Please check your .env configuration."
    if response.status_code == 404:
        return f"I couldn't find weather data for '{city}'. Could you check the city name?"
    if response.status_code != 200:
        return f"The weather service returned an unexpected error (status {response.status_code})."

    try:
        data = response.json()
        description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        return (
            f"The weather in {city.title()} is currently {description}, "
            f"with a temperature of {temp}°C, feeling like {feels_like}°C, "
            f"and {humidity}% humidity."
        )
    except (KeyError, IndexError, ValueError) as exc:
        return f"I received an unexpected response from the weather service ({exc})."
