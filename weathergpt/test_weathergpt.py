"""
test_weathergpt.py
------------------
Simple test script to verify all modules work correctly
WITHOUT needing to open the browser.

Run this with:
    python test_weathergpt.py

What it tests:
  1. Intent detector  – are keywords being detected correctly?
  2. Alert engine     – are thresholds triggering correctly?
  3. Response builder – are responses being built?
  4. Weather API      – can we reach Open-Meteo? (needs internet)

These are called UNIT TESTS — they test one small piece at a time.
"""

import sys
import os

# Add the weathergpt folder to Python's search path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from utils.intent_detector  import detect_intent
from utils.alert_engine     import check_alerts, get_alert_summary
from utils.response_builder import build_response

# ── ANSI color codes for terminal output ────────────────────────────────────
GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"
BOLD  = "\033[1m"

passed = 0
failed = 0


def test(name: str, result, expected):
    """Helper: checks result == expected and prints pass/fail."""
    global passed, failed
    if result == expected:
        print(f"  {GREEN}✅ PASS{RESET} | {name}")
        passed += 1
    else:
        print(f"  {RED}❌ FAIL{RESET} | {name}")
        print(f"       Expected: {expected!r}")
        print(f"       Got:      {result!r}")
        failed += 1


# ═════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}=== TEST 1: Intent Detector ==={RESET}")
# ═════════════════════════════════════════════════════════════════════════════

test("'hello' → greeting",
     detect_intent("hello"),                              "greeting")
test("'hi there' → greeting",
     detect_intent("hi there"),                           "greeting")
test("'What is the temperature?' → temperature",
     detect_intent("What is the temperature?"),           "temperature")
test("'How hot is it?' → temperature",
     detect_intent("How hot is it?"),                     "temperature")
test("'Will it rain today?' → rain",
     detect_intent("Will it rain today?"),                "rain")
test("'Should I carry an umbrella?' → rain",
     detect_intent("Should I carry an umbrella?"),        "rain")
test("'How humid is it?' → humidity",
     detect_intent("How humid is it?"),                   "humidity")
test("'What is the wind speed?' → wind",
     detect_intent("What is the wind speed?"),            "wind")
test("'Show me the 7-day forecast' → forecast",
     detect_intent("Show me the 7-day forecast"),         "forecast")
test("'What about tomorrow?' → forecast",
     detect_intent("What about tomorrow?"),               "forecast")
test("'What is the UV index?' → uv_index",
     detect_intent("What is the UV index?"),              "uv_index")
test("'Any weather alerts?' → alerts",
     detect_intent("Any weather alerts?"),                "alerts")
test("'What is climate change?' → climate_info",
     detect_intent("What is climate change?"),            "climate_info")
test("'help' → help",
     detect_intent("help"),                               "help")
test("'asdfghjkl' → unknown",
     detect_intent("asdfghjkl"),                         "unknown")
test("Case insensitive: 'RAIN' → rain",
     detect_intent("RAIN"),                               "rain")


# ═════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}=== TEST 2: Alert Engine ==={RESET}")
# ═════════════════════════════════════════════════════════════════════════════

# Mock weather data (fake numbers to test threshold logic)
safe_weather = {
    "temperature": 28,
    "humidity":    60,
    "wind_speed":  15,
    "uv_index":    5,
    "rain":        0,
}
safe_forecast = [
    {"rain_probability": 20},
    {"rain_probability": 10},
]

extreme_weather = {
    "temperature": 42,    # > 40 → danger
    "humidity":    95,    # > 90 → watch
    "wind_speed":  70,    # > 60 → danger
    "uv_index":    11,    # > 10 → danger
    "rain":        5,
}
extreme_forecast = [
    {"rain_probability": 85},  # > 80 → warning
    {"rain_probability": 90},  # > 80 → watch
]

cold_weather = {
    "temperature": -5,    # < 0 → danger
    "humidity":    40,
    "wind_speed":  10,
    "uv_index":    1,
    "rain":        0,
}

safe_alerts    = check_alerts(safe_weather,    safe_forecast)
extreme_alerts = check_alerts(extreme_weather, extreme_forecast)
cold_alerts    = check_alerts(cold_weather,    [])

test("Safe weather → 0 alerts",
     len(safe_alerts),    0)
test("Extreme weather → at least 4 alerts",
     len(extreme_alerts) >= 4, True)
test("Cold weather → at least 1 alert",
     len(cold_alerts) >= 1,    True)
test("Safe weather summary starts with ✅",
     get_alert_summary(safe_alerts).startswith("✅"), True)
test("Extreme weather summary starts with ⚠️",
     get_alert_summary(extreme_alerts).startswith("⚠️"), True)

# Check that extreme heat alert is 'danger' severity
danger_alerts = [a for a in extreme_alerts if a["severity"] == "danger"]
test("At least one danger alert in extreme weather",
     len(danger_alerts) >= 1, True)


# ═════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}=== TEST 3: Response Builder ==={RESET}")
# ═════════════════════════════════════════════════════════════════════════════

mock_weather_data = {
    "error":    None,
    "location": {"name": "TestCity", "country": "TC",
                 "latitude": 0.0, "longitude": 0.0, "timezone": "UTC"},
    "current":  {
        "temperature":   28,
        "feels_like":    30,
        "humidity":      70,
        "wind_speed":    20,
        "wind_direction":180,
        "uv_index":      6,
        "rain":          0,
        "precipitation": 0,
        "is_day":        1,
        "description":   "☀️ Clear sky",
        "weather_code":  0,
    },
    "forecast": [
        {"date": "2026-10-20", "temp_max": 32, "temp_min": 24,
         "precipitation": 0, "rain_probability": 10,
         "description": "☀️ Clear sky", "wind_speed_max": 20, "uv_index_max": 7},
        {"date": "2026-10-21", "temp_max": 30, "temp_min": 22,
         "precipitation": 2, "rain_probability": 55,
         "description": "🌧️ Moderate rain", "wind_speed_max": 25, "uv_index_max": 5},
    ],
}

greeting_resp = build_response("greeting", {}, "TestCity")
temp_resp     = build_response("temperature", mock_weather_data, "TestCity")
rain_resp     = build_response("rain",        mock_weather_data, "TestCity")
forecast_resp = build_response("forecast",    mock_weather_data, "TestCity")
climate_resp  = build_response("climate_info",mock_weather_data, "TestCity")
unknown_resp  = build_response("unknown",     mock_weather_data, "TestCity")

test("Greeting response contains 'WeatherGPT'",
     "WeatherGPT" in greeting_resp, True)
test("Temperature response contains '28°C'",
     "28°C" in temp_resp, True)
test("Temperature response contains 'TestCity'",
     "TestCity" in temp_resp, True)
test("Rain response contains 'probability'",
     "probability" in rain_resp.lower(), True)
test("Forecast response contains 'Forecast'",
     "Forecast" in forecast_resp, True)
test("Climate info contains 'Weather'",
     "Weather" in climate_resp, True)
test("Unknown intent returns fallback message",
     "not sure" in unknown_resp.lower() or "understand" in unknown_resp.lower(), True)


# ═════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}=== TEST 4: Weather API (needs internet) ==={RESET}")
# ═════════════════════════════════════════════════════════════════════════════
try:
    from utils.weather_api import get_full_weather, convert_city_to_coordinates

    # Test with a well-known city
    loc = convert_city_to_coordinates("London")
    test("London geocoding returns a result",
         loc is not None, True)
    if loc:
        test("London latitude is approximately 51.5",
             abs(loc["latitude"] - 51.5) < 0.5, True)
        test("London country is 'United Kingdom'",
             "United" in loc["country"], True)

    # Test invalid city
    bad_loc = convert_city_to_coordinates("XxInvalidCityXx99999")
    test("Invalid city returns None",
         bad_loc is None, True)

    # Full weather fetch for Mumbai
    data = get_full_weather("Mumbai")
    test("get_full_weather('Mumbai') has no error",
         data["error"] is None, True)
    test("Mumbai weather data has 'current' section",
         data["current"] is not None, True)
    test("Mumbai forecast has 7 days",
         len(data["forecast"]) == 7, True)
    test("Mumbai temperature is a number",
         isinstance(data["current"]["temperature"], (int, float)), True)

    print(f"\n  Live weather for Mumbai:")
    print(f"    Temperature: {data['current']['temperature']}°C")
    print(f"    Feels like:  {data['current']['feels_like']}°C")
    print(f"    Condition:   {data['current']['description']}")
    print(f"    Humidity:    {data['current']['humidity']}%")

except Exception as e:
    print(f"  {RED}⚠️ API test failed (check internet): {e}{RESET}")

# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}{'='*50}{RESET}")
print(f"{BOLD}RESULTS: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET}")
if failed == 0:
    print(f"{GREEN}{BOLD}🎉 All tests passed! The app is ready to run.{RESET}")
else:
    print(f"{RED}⚠️  Some tests failed. Check the output above.{RESET}")
print(f"{'='*50}\n")
