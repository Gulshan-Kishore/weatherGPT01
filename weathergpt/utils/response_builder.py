"""
response_builder.py
--------------------
Takes an intent and weather data and builds a natural-language
response to show the user in the chat.

Think of this as the "mouth" of the chatbot.  The intent_detector
tells us WHAT the user wants.  This file decides WHAT TO SAY.

Algorithm:
  It is a big if/elif block keyed on the intent string.
  Each branch picks out the relevant numbers from the weather data
  and formats them into a clear English sentence.

  This is still entirely rule-based — no language model involved.
"""

from utils.alert_engine import check_alerts, get_alert_summary


def build_response(intent: str, weather_data: dict, city: str) -> str:
    """
    Creates a chat response string based on the detected intent and
    live weather data fetched from the API.

    Parameters
    ----------
    intent       : str  – the intent label from detect_intent()
    weather_data : dict – the dict returned by get_full_weather()
    city         : str  – the city name the user asked about

    Returns
    -------
    str – a Markdown-formatted response string ready to display
    """

    current  = weather_data.get("current",  {})
    forecast = weather_data.get("forecast", [])
    location = weather_data.get("location", {})

    city_display = location.get("name", city)
    country      = location.get("country", "")

    # ── GREETING ─────────────────────────────────────────────────────────────
    if intent == "greeting":
        return (
            f"👋 Hello! I'm **WeatherGPT** — your friendly weather assistant.\n\n"
            f"I can tell you about:\n"
            f"- 🌡️ Temperature & 'feels like'\n"
            f"- 🌧️ Rain probability\n"
            f"- 💧 Humidity\n"
            f"- 💨 Wind speed\n"
            f"- 📅 7-day forecast\n"
            f"- ☀️ UV index\n"
            f"- ⚠️ Weather alerts\n"
            f"- 🌍 Climate info\n\n"
            f"Just type a city name in the sidebar and ask me anything!"
        )

    # ── HELP ─────────────────────────────────────────────────────────────────
    if intent == "help":
        return (
            f"❓ **How to use WeatherGPT:**\n\n"
            f"1. **Enter a city** in the left sidebar.\n"
            f"2. **Ask a question** like:\n"
            f"   - *'What is the temperature in {city_display}?'*\n"
            f"   - *'Will it rain tomorrow?'*\n"
            f"   - *'How humid is it?'*\n"
            f"   - *'Show me the 7-day forecast'*\n"
            f"   - *'Are there any weather alerts?'*\n"
            f"   - *'What is climate change?'*\n\n"
            f"**Note:** I use real-time data from Open-Meteo API and "
            f"keyword matching to answer your questions — I am not a "
            f"generative AI model, but I give accurate real weather data!"
        )

    # ── No weather data available yet ────────────────────────────────────────
    if not current:
        return (
            f"🏙️ Please enter a **city name** in the sidebar first, then ask "
            f"your weather question!"
        )

    temp       = current.get("temperature", "N/A")
    feels_like = current.get("feels_like",  "N/A")
    humidity   = current.get("humidity",    "N/A")
    wind       = current.get("wind_speed",  "N/A")
    uv         = current.get("uv_index",    "N/A")
    rain       = current.get("rain",        0)
    desc       = current.get("description", "")

    # ── TEMPERATURE ──────────────────────────────────────────────────────────
    if intent == "temperature":
        comfort = ""
        if isinstance(temp, (int, float)):
            if temp >= 35:
                comfort = "🔥 It's scorching hot — stay hydrated!"
            elif temp >= 25:
                comfort = "😊 Quite warm — light clothing recommended."
            elif temp >= 15:
                comfort = "🌤️ Comfortable temperature."
            elif temp >= 5:
                comfort = "🧥 A bit cold — wear a jacket."
            else:
                comfort = "🥶 Very cold — bundle up well!"

        return (
            f"🌡️ **Current weather in {city_display}, {country}:**\n\n"
            f"- **Temperature:** {temp}°C\n"
            f"- **Feels like:** {feels_like}°C\n"
            f"- **Condition:** {desc}\n"
            f"- **Humidity:** {humidity}%\n\n"
            f"{comfort}"
        )

    # ── RAIN ─────────────────────────────────────────────────────────────────
    if intent == "rain":
        # Get today's and tomorrow's rain probability from forecast
        today_rain_prob = forecast[0].get("rain_probability", 0) if forecast else 0
        tmr_rain_prob   = forecast[1].get("rain_probability", 0) if len(forecast) > 1 else 0

        umbrella_advice = ""
        if today_rain_prob > 70:
            umbrella_advice = "☂️ **Definitely carry an umbrella today!**"
        elif today_rain_prob > 40:
            umbrella_advice = "🌂 It might be a good idea to carry an umbrella."
        else:
            umbrella_advice = "✅ Umbrella probably not needed today."

        return (
            f"🌧️ **Rain info for {city_display}, {country}:**\n\n"
            f"- **Current rain:** {rain} mm\n"
            f"- **Today's rain probability:** {today_rain_prob}%\n"
            f"- **Tomorrow's rain probability:** {tmr_rain_prob}%\n"
            f"- **Current condition:** {desc}\n\n"
            f"{umbrella_advice}"
        )

    # ── HUMIDITY ─────────────────────────────────────────────────────────────
    if intent == "humidity":
        comfort = ""
        if isinstance(humidity, (int, float)):
            if humidity > 80:
                comfort = "💦 Very high humidity — feels muggy and uncomfortable."
            elif humidity > 60:
                comfort = "😅 Moderately humid."
            elif humidity > 30:
                comfort = "😊 Comfortable humidity level."
            else:
                comfort = "🏜️ Quite dry — stay hydrated!"

        return (
            f"💧 **Humidity in {city_display}, {country}:**\n\n"
            f"- **Relative humidity:** {humidity}%\n"
            f"- **Temperature:** {temp}°C  |  **Feels like:** {feels_like}°C\n\n"
            f"{comfort}\n\n"
            f"💡 *High humidity makes the same temperature feel hotter because "
            f"your sweat cannot evaporate as easily.*"
        )

    # ── WIND ─────────────────────────────────────────────────────────────────
    if intent == "wind":
        wind_desc = ""
        if isinstance(wind, (int, float)):
            if wind < 5:
                wind_desc = "🍃 Calm — barely any wind."
            elif wind < 20:
                wind_desc = "🌿 Light breeze."
            elif wind < 40:
                wind_desc = "💨 Moderate wind."
            elif wind < 60:
                wind_desc = "🌬️ Strong wind — be careful outdoors."
            else:
                wind_desc = "🌀 Gale-force winds — stay indoors if possible!"

        # Wind direction in compass points
        wind_dir_num = current.get("wind_direction", 0)
        compass_dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        compass = compass_dirs[round(wind_dir_num / 45) % 8]

        return (
            f"💨 **Wind conditions in {city_display}, {country}:**\n\n"
            f"- **Wind speed:** {wind} km/h\n"
            f"- **Wind direction:** {compass} ({wind_dir_num}°)\n\n"
            f"{wind_desc}"
        )

    # ── FORECAST ─────────────────────────────────────────────────────────────
    if intent == "forecast":
        if not forecast:
            return "📅 Forecast data is not available right now. Please try again."

        lines = [f"📅 **7-Day Forecast for {city_display}, {country}:**\n"]
        for day in forecast[:7]:
            date    = day.get("date", "")
            mx      = day.get("temp_max", "?")
            mn      = day.get("temp_min", "?")
            desc_d  = day.get("description", "")
            rain_p  = day.get("rain_probability", 0)
            lines.append(
                f"**{date}** — {desc_d}  "
                f"| 🌡️ {mn}°C – {mx}°C  "
                f"| 🌧️ {rain_p}% rain"
            )

        lines.append(
            "\n💡 *Forecast data comes directly from Open-Meteo API. "
            "Accuracy decreases beyond 3 days.*"
        )
        return "\n".join(lines)

    # ── UV INDEX ─────────────────────────────────────────────────────────────
    if intent == "uv_index":
        uv_desc = ""
        if isinstance(uv, (int, float)):
            if uv <= 2:
                uv_desc = "🟢 Low — no protection needed."
            elif uv <= 5:
                uv_desc = "🟡 Moderate — wear sunscreen."
            elif uv <= 7:
                uv_desc = "🟠 High — use SPF 30+ and hat."
            elif uv <= 10:
                uv_desc = "🔴 Very high — avoid midday sun."
            else:
                uv_desc = "🟣 Extreme — take full precautions!"

        return (
            f"☀️ **UV Index in {city_display}, {country}:**\n\n"
            f"- **UV Index:** {uv}\n"
            f"- **Risk level:** {uv_desc}\n\n"
            f"💡 *UV index above 3 = apply sunscreen; above 8 = seek shade.*"
        )

    # ── ALERTS ───────────────────────────────────────────────────────────────
    if intent == "alerts":
        alerts = check_alerts(current, forecast)
        summary = get_alert_summary(alerts)

        if not alerts:
            return f"✅ **No active alerts for {city_display}, {country}.**\n\n{summary}"

        lines = [f"⚠️ **Weather Alerts for {city_display}, {country}:**\n",
                 summary, ""]
        for alert in alerts:
            lines.append(
                f"{alert['icon']} **{alert['title']}** *(Severity: {alert['severity']})*\n"
                f"  {alert['message']}\n"
            )
        return "\n".join(lines)

    # ── CLIMATE INFO ─────────────────────────────────────────────────────────
    if intent == "climate_info":
        return (
            f"🌍 **Weather vs. Climate — What's the Difference?**\n\n"
            f"**Weather** is the short-term atmospheric condition at a specific "
            f"place and time. For example: 'It is raining in Mumbai today.' "
            f"Weather changes from hour to hour and day to day.\n\n"
            f"**Climate** is the long-term pattern of weather in a region, "
            f"averaged over 30+ years. For example: 'Mumbai has a tropical "
            f"climate with heavy monsoons from June to September.'\n\n"
            f"🎙️ **Easy memory trick:** "
            f"*Climate is what you EXPECT; weather is what you GET.*\n\n"
            f"---\n"
            f"**Climate Change** refers to long-term shifts in global temperatures "
            f"and weather patterns, largely driven by human activities like burning "
            f"fossil fuels since the Industrial Revolution (mid-1800s).\n\n"
            f"**Key facts:**\n"
            f"- 🌡️ Global average temperature has risen ~1.1°C since pre-industrial times\n"
            f"- 🧊 Arctic sea ice is shrinking at ~13% per decade\n"
            f"- 🌊 Sea levels are rising ~3.3 mm per year\n"
            f"- 📚 Source: IPCC (Intergovernmental Panel on Climate Change)"
        )

    # ── UNKNOWN / FALLBACK ────────────────────────────────────────────────────
    return (
        f"🤔 I'm not sure I understood that question. Here are some things "
        f"I can answer for **{city_display}**:\n\n"
        f"- *'What is the temperature?'*\n"
        f"- *'Will it rain today?'*\n"
        f"- *'How humid is it?'*\n"
        f"- *'What is the wind speed?'*\n"
        f"- *'Show the 7-day forecast'*\n"
        f"- *'Any weather alerts?'*\n"
        f"- *'What is the UV index?'*\n"
        f"- *'What is climate change?'*\n\n"
        f"Type `help` to see all options."
    )
