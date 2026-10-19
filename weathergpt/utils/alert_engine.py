"""
alert_engine.py
---------------
Checks weather data against fixed thresholds and generates
plain-English weather alert messages.

This is called a THRESHOLD-BASED alert system — the simplest and most
interpretable kind of rule system.

Algorithm:
  For each weather condition, we set two numbers: a safe range.
  If the actual value EXCEEDS those numbers, we fire an alert.

  Example: if temperature > 40 °C → "Extreme heat!" alert
           if temperature < 0 °C  → "Freezing cold!" alert

Threshold table (all values are configurable at the top of this file):
┌─────────────────────────┬────────────┬──────────────────────────┐
│ Condition               │ Threshold  │ Severity                 │
├─────────────────────────┼────────────┼──────────────────────────┤
│ Temperature (°C)        │ > 40       │ 🔴 Danger (Extreme heat) │
│ Temperature (°C)        │ > 35       │ 🟠 Warning (Very hot)    │
│ Temperature (°C)        │ < 0        │ 🔴 Danger (Freezing)     │
│ Temperature (°C)        │ < 5        │ 🟡 Watch  (Very cold)    │
│ Rain probability (%)    │ > 80       │ 🟠 Warning (Heavy rain)  │
│ Rain probability (%)    │ > 50       │ 🟡 Watch  (Moderate rain)│
│ Wind speed (km/h)       │ > 60       │ 🔴 Danger (Gale)         │
│ Wind speed (km/h)       │ > 40       │ 🟠 Warning (Strong wind) │
│ UV Index                │ > 10       │ 🔴 Danger (Extreme UV)   │
│ UV Index                │ > 7        │ 🟠 Warning (High UV)     │
│ Humidity (%)            │ > 90       │ 🟡 Watch  (Very humid)   │
└─────────────────────────┴────────────┴──────────────────────────┘
"""

# ── Configurable thresholds ──────────────────────────────────────────────────
TEMP_EXTREME_HOT  = 40    # °C – Danger level
TEMP_WARNING_HOT  = 35    # °C – Warning level
TEMP_EXTREME_COLD = 0     # °C – Freezing danger
TEMP_WARNING_COLD = 5     # °C – Very cold warning

RAIN_DANGER   = 80        # % probability
RAIN_WARNING  = 50        # % probability

WIND_DANGER   = 60        # km/h
WIND_WARNING  = 40        # km/h

UV_DANGER     = 10        # UV index units
UV_WARNING    = 7

HUMIDITY_HIGH = 90        # %


def check_alerts(current: dict, forecast: list) -> list:
    """
    Checks all weather values against thresholds and returns a list of alerts.

    Each alert is a dictionary with:
      "severity" : "danger" | "warning" | "watch"
      "icon"     : emoji icon for the alert type
      "title"    : short title
      "message"  : full explanation sentence

    Algorithm (step-by-step):
      Step 1 – Start with an empty list of alerts
      Step 2 – Check current temperature against hot/cold thresholds
      Step 3 – Check today's and tomorrow's rain probability
      Step 4 – Check current wind speed
      Step 5 – Check UV index
      Step 6 – Check humidity
      Step 7 – Return the list (may be empty if all is safe)

    Parameters
    ----------
    current  : dict  – output from get_current_weather()
    forecast : list  – output from get_forecast() (list of day dicts)

    Returns
    -------
    list of alert dicts
    """

    alerts = []   # Start with no alerts

    temp      = current.get("temperature", 0)
    humidity  = current.get("humidity", 0)
    wind      = current.get("wind_speed", 0)
    uv        = current.get("uv_index", 0)

    # ── Temperature checks ───────────────────────────────────────────────────
    if temp > TEMP_EXTREME_HOT:
        alerts.append({
            "severity": "danger",
            "icon":     "🔴",
            "title":    "Extreme Heat",
            "message":  f"Current temperature is {temp}°C — dangerously hot! "
                        f"Stay indoors, drink plenty of water, and avoid outdoor "
                        f"activity between 11 AM and 4 PM.",
        })
    elif temp > TEMP_WARNING_HOT:
        alerts.append({
            "severity": "warning",
            "icon":     "🟠",
            "title":    "High Temperature",
            "message":  f"Temperature is {temp}°C — very hot. Stay hydrated and "
                        f"use sunscreen if going outside.",
        })

    if temp < TEMP_EXTREME_COLD:
        alerts.append({
            "severity": "danger",
            "icon":     "🔴",
            "title":    "Freezing Temperatures",
            "message":  f"Temperature is {temp}°C — below freezing! Risk of "
                        f"frostbite. Wear heavy layers and cover extremities.",
        })
    elif temp < TEMP_WARNING_COLD:
        alerts.append({
            "severity": "warning",
            "icon":     "🟠",
            "title":    "Very Cold",
            "message":  f"Temperature is {temp}°C — very cold. Wear warm clothes "
                        f"and be careful on icy surfaces.",
        })

    # ── Rain probability check (today + tomorrow from forecast) ─────────────
    if len(forecast) > 0:
        today_rain = forecast[0].get("rain_probability", 0)
        if today_rain > RAIN_DANGER:
            alerts.append({
                "severity": "warning",
                "icon":     "🟠",
                "title":    "Heavy Rain Expected Today",
                "message":  f"Rain probability today is {today_rain}%. Carry an "
                            f"umbrella and watch for flooding in low-lying areas.",
            })
        elif today_rain > RAIN_WARNING:
            alerts.append({
                "severity": "watch",
                "icon":     "🟡",
                "title":    "Moderate Rain Possible Today",
                "message":  f"There is a {today_rain}% chance of rain today. "
                            f"Consider carrying an umbrella.",
            })

    if len(forecast) > 1:
        tmr_rain = forecast[1].get("rain_probability", 0)
        if tmr_rain > RAIN_DANGER:
            alerts.append({
                "severity": "watch",
                "icon":     "🟡",
                "title":    "Heavy Rain Expected Tomorrow",
                "message":  f"Rain probability tomorrow is {tmr_rain}%. Plan ahead.",
            })

    # ── Wind speed check ─────────────────────────────────────────────────────
    if wind > WIND_DANGER:
        alerts.append({
            "severity": "danger",
            "icon":     "🔴",
            "title":    "Gale-Force Winds",
            "message":  f"Wind speed is {wind} km/h — dangerous! Avoid being "
                        f"outdoors, secure loose objects.",
        })
    elif wind > WIND_WARNING:
        alerts.append({
            "severity": "warning",
            "icon":     "🟠",
            "title":    "Strong Winds",
            "message":  f"Wind speed is {wind} km/h. Be cautious while driving "
                        f"or riding a two-wheeler.",
        })

    # ── UV Index check ───────────────────────────────────────────────────────
    if uv > UV_DANGER:
        alerts.append({
            "severity": "danger",
            "icon":     "🔴",
            "title":    "Extreme UV Index",
            "message":  f"UV Index is {uv} — extremely high! Avoid sun exposure. "
                        f"If outside, use SPF 50+ sunscreen and protective clothing.",
        })
    elif uv > UV_WARNING:
        alerts.append({
            "severity": "warning",
            "icon":     "🟠",
            "title":    "High UV Index",
            "message":  f"UV Index is {uv}. Apply sunscreen and wear sunglasses "
                        f"when outdoors.",
        })

    # ── Humidity check ───────────────────────────────────────────────────────
    if humidity > HUMIDITY_HIGH:
        alerts.append({
            "severity": "watch",
            "icon":     "🟡",
            "title":    "Very High Humidity",
            "message":  f"Humidity is {humidity}% — very muggy. Stay hydrated. "
                        f"Heat feels worse in high humidity.",
        })

    return alerts


def get_alert_summary(alerts: list) -> str:
    """
    Returns a single summary sentence about the alert situation.

    Parameters
    ----------
    alerts : list – output from check_alerts()

    Returns
    -------
    str – e.g. "⚠️ 3 active alerts (1 danger, 2 warnings)."
    """
    if not alerts:
        return "✅ No active weather alerts. Conditions look safe!"

    danger_count  = sum(1 for a in alerts if a["severity"] == "danger")
    warning_count = sum(1 for a in alerts if a["severity"] == "warning")
    watch_count   = sum(1 for a in alerts if a["severity"] == "watch")

    parts = []
    if danger_count:
        parts.append(f"{danger_count} 🔴 danger")
    if warning_count:
        parts.append(f"{warning_count} 🟠 warning")
    if watch_count:
        parts.append(f"{watch_count} 🟡 watch")

    return f"⚠️ {len(alerts)} active alert(s): {', '.join(parts)}."
