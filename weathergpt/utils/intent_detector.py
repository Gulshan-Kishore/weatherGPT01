"""
intent_detector.py
------------------
Figures out WHAT the user is asking about by scanning their message
for keywords.  This is called a RULE-BASED intent classifier.

It is NOT a trained AI model — it is just a series of if/elif checks
using Python's "in" operator.

Why rule-based?
  • Easy to understand and change
  • Works instantly (no model loading time)
  • Transparent: you can read exactly what it does
  • Good enough for a focused domain like weather Q&A

How it works (algorithm):
  1. Convert the user's message to lowercase (so "RAIN" and "rain" match)
  2. Check each keyword group one by one using if/elif
  3. Return the first intent whose keywords appear in the message
  4. If nothing matches, return the "unknown" intent

Intents supported:
  • temperature   – questions about how hot/cold it is
  • rain          – questions about rain, drizzle, umbrella
  • humidity      – questions about humidity / moisture
  • wind          – questions about wind speed/direction
  • forecast      – questions about tomorrow or the coming days
  • uv_index      – questions about UV rays / sunscreen
  • alerts        – questions about weather warnings
  • climate_info  – questions about what weather/climate means
  • greeting      – hello, hi, hey
  • help          – what can you do, help
  • unknown       – anything else
"""


def detect_intent(user_message: str) -> str:
    """
    Scans the user's message and returns an intent label (string).

    Algorithm:
      Step 1 – Lowercase the message (case-insensitive matching)
      Step 2 – Define keyword groups for each intent
      Step 3 – Check if ANY keyword from a group appears in the message
      Step 4 – Return the matching intent name
      Step 5 – If no group matches, return "unknown"

    Parameters
    ----------
    user_message : str
        The raw text typed by the user, e.g. "Will it rain tomorrow?"

    Returns
    -------
    str – one of the intent labels listed above
    """

    # Step 1: Make everything lowercase so "Rain" == "rain"
    msg = user_message.lower()

    # ── Step 2 & 3: Check each intent group ─────────────────────────────────

    # GREETING intent
    greeting_keywords = ["hello", "hi", "hey", "good morning", "good evening",
                         "good afternoon", "howdy", "namaste", "greetings"]
    if any(word in msg for word in greeting_keywords):
        return "greeting"

    # HELP intent
    help_keywords = ["help", "what can you do", "what do you know",
                     "how to use", "commands", "options", "features"]
    if any(word in msg for word in help_keywords):
        return "help"

    # TEMPERATURE intent
    temperature_keywords = ["temperature", "temp", "hot", "cold", "warm",
                            "cool", "heat", "degrees", "celsius", "feels like",
                            "how warm", "how cold", "freezing", "burning"]
    if any(word in msg for word in temperature_keywords):
        return "temperature"

    # RAIN intent
    rain_keywords = ["rain", "raining", "rainy", "drizzle", "shower",
                     "umbrella", "wet", "precipitation", "storm", "monsoon",
                     "flood", "downpour"]
    if any(word in msg for word in rain_keywords):
        return "rain"

    # HUMIDITY intent
    humidity_keywords = ["humidity", "humid", "moisture", "damp", "muggy",
                         "dry", "sticky"]
    if any(word in msg for word in humidity_keywords):
        return "humidity"

    # WIND intent
    wind_keywords = ["wind", "windy", "breeze", "breezy", "gust", "gale",
                     "windspeed", "wind speed", "wind direction"]
    if any(word in msg for word in wind_keywords):
        return "wind"

    # FORECAST intent  (must check BEFORE "tomorrow" alone to catch context)
    forecast_keywords = ["forecast", "tomorrow", "next week", "this week",
                         "coming days", "next days", "week ahead",
                         "7 day", "seven day", "5 day", "five day",
                         "future", "prediction", "predict", "upcoming",
                         "sunday", "monday", "tuesday", "wednesday",
                         "thursday", "friday", "saturday"]
    if any(word in msg for word in forecast_keywords):
        return "forecast"

    # UV INDEX intent
    uv_keywords = ["uv", "uv index", "ultraviolet", "sunscreen", "sunburn",
                   "sun protection", "spf"]
    if any(word in msg for word in uv_keywords):
        return "uv_index"

    # ALERTS intent
    alert_keywords = ["alert", "warning", "danger", "severe", "extreme",
                      "unsafe", "hazard", "caution", "advisory"]
    if any(word in msg for word in alert_keywords):
        return "alerts"

    # CLIMATE INFO intent
    climate_keywords = ["climate", "difference between weather and climate",
                        "what is weather", "what is climate", "climate change",
                        "global warming", "season", "seasons"]
    if any(word in msg for word in climate_keywords):
        return "climate_info"

    # General weather check (e.g., "What's the weather in Delhi?")
    weather_keywords = ["weather", "condition", "outside", "sky", "cloudy",
                        "cloud", "sunny", "sunshine", "snow", "fog", "foggy",
                        "thunder", "lightning", "overcast", "clear"]
    if any(word in msg for word in weather_keywords):
        return "temperature"   # Default to showing temperature/conditions

    # Step 5: Nothing matched → unknown
    return "unknown"


def get_intent_display_name(intent: str) -> str:
    """
    Returns a human-friendly label for a given intent string.
    Used only for display / debugging purposes.
    """
    labels = {
        "temperature":  "🌡️ Temperature",
        "rain":         "🌧️ Rain",
        "humidity":     "💧 Humidity",
        "wind":         "💨 Wind",
        "forecast":     "📅 Forecast",
        "uv_index":     "☀️ UV Index",
        "alerts":       "⚠️ Weather Alerts",
        "climate_info": "🌍 Climate Info",
        "greeting":     "👋 Greeting",
        "help":         "❓ Help",
        "unknown":      "🤷 Unknown",
    }
    return labels.get(intent, "Unknown")
