"""
weather_api.py
--------------
Handles all communication with the Open-Meteo API and the
Geocoding API.  Both are completely FREE and need NO API key.

What this file does (beginner explanation):
  1. convert_city_to_coordinates()  →  turns a city name like "Mumbai"
     into latitude and longitude numbers (e.g. 19.07, 72.87)
  2. get_current_weather()          →  asks Open-Meteo for right-now
     weather values for those coordinates
  3. get_forecast()                 →  asks Open-Meteo for the next
     7 days of weather data
  4. get_full_weather()             →  calls all of the above and
     packages everything into one neat Python dictionary

APIs used:
  • https://geocoding-api.open-meteo.com  – city → lat/lon
  • https://api.open-meteo.com            – weather data
"""

import requests  # pip install requests  – lets Python talk to the internet

# ── How long (seconds) to wait before giving up on a slow API call ──────────
REQUEST_TIMEOUT = 10

# ── Human-readable labels for Open-Meteo WMO weather codes ──────────────────
# WMO codes are international standard numbers that describe weather conditions
WMO_CODES = {
    0:  "☀️ Clear sky",
    1:  "🌤️ Mainly clear",
    2:  "⛅ Partly cloudy",
    3:  "☁️ Overcast",
    45: "🌫️ Foggy",
    48: "🌫️ Freezing fog",
    51: "🌦️ Light drizzle",
    53: "🌦️ Moderate drizzle",
    55: "🌧️ Dense drizzle",
    61: "🌧️ Slight rain",
    63: "🌧️ Moderate rain",
    65: "🌧️ Heavy rain",
    71: "❄️ Slight snow",
    73: "❄️ Moderate snow",
    75: "❄️ Heavy snow",
    80: "🌦️ Slight rain showers",
    81: "🌧️ Moderate rain showers",
    82: "⛈️ Violent rain showers",
    95: "⛈️ Thunderstorm",
    96: "⛈️ Thunderstorm with hail",
    99: "⛈️ Heavy thunderstorm with hail",
}


def convert_city_to_coordinates(city_name: str) -> dict:
    """
    Converts a city name into its GPS coordinates (latitude & longitude).

    Algorithm (step-by-step):
      Step 1 – Build the URL for the geocoding API with the city name.
      Step 2 – Send a GET request (like opening a link in your browser).
      Step 3 – Read the JSON response (JSON is just a Python dictionary
                from the internet).
      Step 4 – If the API found results, return the first match.
      Step 5 – If no results, return None so the caller knows the city
                was not found.

    Parameters
    ----------
    city_name : str   – e.g. "Bangalore" or "London"

    Returns
    -------
    dict with keys: name, latitude, longitude, country, timezone
    OR returns None if the city was not found.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"

    # "params" are the query-string values added to the URL automatically
    params = {
        "name":     city_name,
        "count":    1,          # We only want the best match
        "language": "en",
        "format":   "json",
    }

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()        # raises an error for 4xx/5xx codes
        data = response.json()

        # The API returns a list called "results"; check if it is non-empty
        if "results" not in data or len(data["results"]) == 0:
            return None  # City not found

        result = data["results"][0]        # Take the very first (best) match
        return {
            "name":      result.get("name", city_name),
            "latitude":  result["latitude"],
            "longitude": result["longitude"],
            "country":   result.get("country", "Unknown"),
            "timezone":  result.get("timezone", "UTC"),
        }

    except requests.exceptions.ConnectionError:
        # This happens when there is no internet connection
        raise ConnectionError("No internet connection. Please check your network.")

    except requests.exceptions.Timeout:
        # This happens when the API takes too long to respond
        raise TimeoutError("The weather server took too long to respond. Try again.")

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"API error: {e}")


def get_current_weather(latitude: float, longitude: float, timezone: str) -> dict:
    """
    Fetches the CURRENT weather for a given latitude/longitude.

    Algorithm (step-by-step):
      Step 1 – Tell Open-Meteo which variables we want (temperature,
                humidity, wind speed, etc.)
      Step 2 – Send the GET request.
      Step 3 – Parse the JSON response.
      Step 4 – Pull out the values from the "current" section.
      Step 5 – Convert the WMO weather code to a human-readable label.
      Step 6 – Return a clean dictionary of all values.

    Parameters
    ----------
    latitude, longitude : float  – GPS coordinates from geocoding
    timezone            : str    – e.g. "Asia/Kolkata"

    Returns
    -------
    dict with current weather values
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude":          latitude,
        "longitude":         longitude,
        "current":           [
            "temperature_2m",          # Temperature at 2 metres height (°C)
            "relative_humidity_2m",    # Relative humidity (%)
            "apparent_temperature",    # "Feels like" temperature (°C)
            "precipitation",           # Current precipitation (mm)
            "rain",                    # Rain amount (mm)
            "weathercode",             # WMO condition code
            "windspeed_10m",           # Wind speed at 10 m height (km/h)
            "winddirection_10m",       # Wind direction (degrees 0-360)
            "uv_index",                # UV Index
            "is_day",                  # 1 = daytime, 0 = night
        ],
        "timezone":          timezone,
        "forecast_days":     1,
    }

    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    c = data["current"]          # Shorthand for the "current" section
    units = data["current_units"]

    wmo_code    = c.get("weathercode", 0)
    description = WMO_CODES.get(wmo_code, "🌡️ Unknown condition")

    return {
        "temperature":        round(c.get("temperature_2m", 0), 1),
        "feels_like":         round(c.get("apparent_temperature", 0), 1),
        "humidity":           c.get("relative_humidity_2m", 0),
        "precipitation":      c.get("precipitation", 0),
        "rain":               c.get("rain", 0),
        "wind_speed":         round(c.get("windspeed_10m", 0), 1),
        "wind_direction":     c.get("winddirection_10m", 0),
        "uv_index":           c.get("uv_index", 0),
        "is_day":             c.get("is_day", 1),
        "weather_code":       wmo_code,
        "description":        description,
        "temp_unit":          units.get("temperature_2m", "°C"),
    }


def get_forecast(latitude: float, longitude: float, timezone: str) -> list:
    """
    Fetches a 7-day daily weather forecast.

    Algorithm (step-by-step):
      Step 1 – Request 7 days of DAILY data from Open-Meteo.
      Step 2 – Parse the JSON response.
      Step 3 – The API returns separate parallel lists (one list of dates,
                one list of max temps, one list of min temps, etc.).
      Step 4 – We zip those lists together so day 0 gets all its values,
                day 1 gets all its values, and so on.
      Step 5 – Return a list of dictionaries, one per day.

    Parameters
    ----------
    latitude, longitude : float
    timezone            : str

    Returns
    -------
    list of dicts, each dict is one day's forecast
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude":     latitude,
        "longitude":    longitude,
        "daily":        [
            "temperature_2m_max",      # Highest temp of the day (°C)
            "temperature_2m_min",      # Lowest temp of the day (°C)
            "precipitation_sum",       # Total rain for the day (mm)
            "precipitation_probability_max",  # Max rain probability (%)
            "weathercode",             # WMO condition code for the day
            "windspeed_10m_max",       # Peak wind speed (km/h)
            "uv_index_max",            # Peak UV index
        ],
        "timezone":     timezone,
        "forecast_days": 7,
    }

    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    daily = data["daily"]   # This is a dict of parallel lists

    forecast_list = []
    # zip() pairs up matching indices from multiple lists simultaneously
    for i, date in enumerate(daily["time"]):
        wmo_code = daily["weathercode"][i]
        forecast_list.append({
            "date":             date,
            "temp_max":         round(daily["temperature_2m_max"][i], 1),
            "temp_min":         round(daily["temperature_2m_min"][i], 1),
            "precipitation":    round(daily["precipitation_sum"][i] or 0, 1),
            "rain_probability": daily["precipitation_probability_max"][i] or 0,
            "weather_code":     wmo_code,
            "description":      WMO_CODES.get(wmo_code, "Unknown"),
            "wind_speed_max":   round(daily["windspeed_10m_max"][i] or 0, 1),
            "uv_index_max":     daily["uv_index_max"][i] or 0,
        })

    return forecast_list


def get_full_weather(city_name: str) -> dict:
    """
    Master function – calls all helpers and returns everything in one dict.

    This is the ONLY function the rest of the app needs to call.

    Returns a dict with keys:
      "location"  → city info
      "current"   → right-now weather
      "forecast"  → list of 7 days
      "error"     → None if everything worked, or an error message string
    """
    # ── Step 1: Geocode the city ─────────────────────────────────────────────
    location = convert_city_to_coordinates(city_name)

    if location is None:
        return {
            "error":    f"❌ City '{city_name}' was not found. "
                        f"Please check the spelling and try again.",
            "location": None,
            "current":  None,
            "forecast": [],
        }

    lat      = location["latitude"]
    lon      = location["longitude"]
    timezone = location["timezone"]

    # ── Step 2: Get current conditions ───────────────────────────────────────
    current  = get_current_weather(lat, lon, timezone)

    # ── Step 3: Get 7-day forecast ───────────────────────────────────────────
    forecast = get_forecast(lat, lon, timezone)

    return {
        "error":    None,
        "location": location,
        "current":  current,
        "forecast": forecast,
    }
