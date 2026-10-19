"""
app.py  ──  WeatherGPT: Main Streamlit Application
====================================================
This is the entry point of the project.  Run it with:
    streamlit run app.py

What Streamlit does:
  Streamlit turns a normal Python script into a web app.
  Every time the user interacts (clicks, types), Streamlit re-runs this
  script from top to bottom and updates the display.

  st.session_state  →  a special dictionary that PERSISTS between re-runs,
                       so we can keep track of chat history, etc.

Sections in this file:
  1. Page configuration  – title, icon, layout
  2. Session state init  – set up variables that need to survive re-runs
  3. Sidebar             – city input + weather summary card
  4. Main area           – tabbed interface
       Tab 1: 💬 Chat
       Tab 2: 📊 Current Weather
       Tab 3: 📅 Forecast
       Tab 4: ⚠️ Alerts
       Tab 5: 🌍 Climate Info
"""

import streamlit as st
import datetime

# ── Import our custom modules ────────────────────────────────────────────────
from utils.weather_api      import get_full_weather
from utils.intent_detector  import detect_intent, get_intent_display_name
from utils.response_builder import build_response
from utils.alert_engine     import check_alerts, get_alert_summary

# ═══════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIGURATION  (must be the very first Streamlit call)
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="WeatherGPT",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for a cleaner look ────────────────────────────────────────────
st.markdown("""
<style>
    /* Chat bubble styles */
    .user-bubble {
        background-color: #DCF8C6;
        border-radius: 12px 12px 0 12px;
        padding: 10px 14px;
        margin: 6px 0;
        max-width: 75%;
        margin-left: auto;
        color: #1a1a1a;
    }
    .bot-bubble {
        background-color: #F0F2F6;
        border-radius: 12px 12px 12px 0;
        padding: 10px 14px;
        margin: 6px 0;
        max-width: 85%;
        color: #1a1a1a;
    }
    .alert-danger  { background:#FFE0E0; border-left:4px solid #FF4B4B; padding:10px; border-radius:6px; margin:6px 0; }
    .alert-warning { background:#FFF3CD; border-left:4px solid #FFA500; padding:10px; border-radius:6px; margin:6px 0; }
    .alert-watch   { background:#FFF9C4; border-left:4px solid #FFD700; padding:10px; border-radius:6px; margin:6px 0; }
    .metric-box    { background:#F8F9FA; border-radius:10px; padding:15px; text-align:center; }
    .stButton button { width:100%; }
    footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SESSION STATE INITIALISATION
#    st.session_state works like a global dictionary that is NOT cleared
#    between Streamlit re-runs.
# ═══════════════════════════════════════════════════════════════════════════════
def init_session_state():
    """
    Sets up default values in session state on the first run.
    Uses the pattern: if key not in state → set it.
    This ensures we don't reset values on every re-run.
    """
    defaults = {
        "chat_history":   [],   # List of {"role": "user"|"bot", "text": str}
        "weather_data":   None, # The last fetched weather dict
        "current_city":   "",   # The city currently loaded
        "query_history":  [],   # List of recent user queries (text only)
        "is_loading":     False, # True while fetching from API
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_weather(city: str):
    """
    Calls the weather API and stores the result in session_state.

    Algorithm:
      Step 1 – Show a loading spinner so the user knows something is happening
      Step 2 – Call get_full_weather(city) which contacts Open-Meteo
      Step 3 – Store the result (or error) in st.session_state
      Step 4 – Add the bot's response to chat history
    """
    with st.spinner(f"Fetching weather for **{city}** ..."):
        try:
            data = get_full_weather(city)
            st.session_state["weather_data"] = data
            st.session_state["current_city"] = city

            if data["error"]:
                # City not found or network error from API
                bot_text = data["error"]
            else:
                # Build a welcome message using the temperature intent
                bot_text = build_response("temperature", data, city)

        except ConnectionError as e:
            bot_text = f"🔌 **Connection Error:** {e}"
            st.session_state["weather_data"] = None
        except TimeoutError as e:
            bot_text = f"⏳ **Timeout Error:** {e}"
            st.session_state["weather_data"] = None
        except Exception as e:
            bot_text = f"⚠️ **Unexpected Error:** {str(e)}"
            st.session_state["weather_data"] = None

    # Add city-fetch confirmation to chat
    st.session_state["chat_history"].append({
        "role": "bot",
        "text": bot_text,
        "timestamp": datetime.datetime.now().strftime("%H:%M"),
    })


def handle_user_message(user_text: str):
    """
    Processes a user's typed chat message.

    Algorithm:
      Step 1 – Add the user's message to chat history
      Step 2 – Store the query in query_history (for the sidebar)
      Step 3 – Detect the intent using keyword matching
      Step 4 – If weather data is available, build a response
      Step 5 – Handle special intents (greeting/help) without weather data
      Step 6 – Add the bot's response to chat history
    """
    user_text = user_text.strip()
    if not user_text:
        return

    # Step 1 – Save user message
    st.session_state["chat_history"].append({
        "role":      "user",
        "text":      user_text,
        "timestamp": datetime.datetime.now().strftime("%H:%M"),
    })

    # Step 2 – Save to query history (keep last 10)
    st.session_state["query_history"].append(user_text)
    if len(st.session_state["query_history"]) > 10:
        st.session_state["query_history"].pop(0)  # Remove oldest

    # Step 3 – Detect intent
    intent = detect_intent(user_text)

    # Step 4 & 5 – Build response
    weather_data = st.session_state.get("weather_data")
    city         = st.session_state.get("current_city", "your city")

    # Greeting and help work even without weather data
    if intent in ("greeting", "help"):
        bot_text = build_response(intent, weather_data or {}, city)
    elif weather_data is None or weather_data.get("error"):
        bot_text = (
            "🏙️ Please enter a city name in the **left sidebar** first, "
            "then I can answer your weather questions!"
        )
    else:
        bot_text = build_response(intent, weather_data, city)

    # Step 6 – Save bot response
    st.session_state["chat_history"].append({
        "role":      "bot",
        "text":      bot_text,
        "timestamp": datetime.datetime.now().strftime("%H:%M"),
        "intent":    get_intent_display_name(intent),
    })


def render_chat_bubble(message: dict):
    """
    Renders a single chat message as an HTML bubble.
    User messages appear on the RIGHT (green).
    Bot messages appear on the LEFT (grey).
    """
    role      = message["role"]
    text      = message["text"]
    timestamp = message.get("timestamp", "")
    intent    = message.get("intent", "")

    if role == "user":
        st.markdown(
            f'<div class="user-bubble">👤 <b>You</b> <small style="color:#555">({timestamp})</small><br>{text}</div>',
            unsafe_allow_html=True,
        )
    else:
        intent_tag = f' <small style="color:#888">— {intent}</small>' if intent else ""
        st.markdown(
            f'<div class="bot-bubble">⛅ <b>WeatherGPT</b>{intent_tag} <small style="color:#555">({timestamp})</small><br><br>{text}</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image(
        "https://em-content.zobj.net/source/apple/354/sun-behind-rain-cloud_1f326-fe0f.png",
        width=80,
    )
    st.title("⛅ WeatherGPT")
    st.caption("AI-powered weather assistant (rule-based)")

    st.divider()

    # ── City input ───────────────────────────────────────────────────────────
    st.subheader("🏙️ Select City")
    city_input = st.text_input(
        "Enter city name:",
        placeholder="e.g. Mumbai, London, Tokyo",
        key="city_input_field",
    )
    search_btn = st.button("🔍 Get Weather", use_container_width=True)

    # Trigger fetch when button is clicked and a city is entered
    if search_btn and city_input.strip():
        fetch_weather(city_input.strip().title())
        st.rerun()

    # ── Quick city buttons ───────────────────────────────────────────────────
    st.subheader("⚡ Quick Cities")
    quick_cities = ["Mumbai", "Delhi", "Bangalore", "London", "New York", "Tokyo"]
    cols = st.columns(2)
    for i, qcity in enumerate(quick_cities):
        with cols[i % 2]:
            if st.button(qcity, key=f"quick_{qcity}"):
                fetch_weather(qcity)
                st.rerun()

    # ── Current weather summary in sidebar ───────────────────────────────────
    weather_data = st.session_state.get("weather_data")
    if weather_data and not weather_data.get("error"):
        st.divider()
        st.subheader("📊 Quick Stats")
        current  = weather_data["current"]
        location = weather_data["location"]
        st.metric("🏙️ City",        f"{location['name']}, {location['country']}")
        st.metric("🌡️ Temperature", f"{current['temperature']}°C")
        st.metric("💧 Humidity",    f"{current['humidity']}%")
        st.metric("💨 Wind",        f"{current['wind_speed']} km/h")
        st.caption(f"Condition: {current['description']}")

    st.divider()

    # ── Recent query history ─────────────────────────────────────────────────
    query_hist = st.session_state.get("query_history", [])
    if query_hist:
        st.subheader("🕐 Recent Questions")
        for q in reversed(query_hist[-5:]):   # Show latest 5, newest first
            st.caption(f"• {q}")

    # ── Clear chat button ────────────────────────────────────────────────────
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["chat_history"]  = []
        st.session_state["query_history"] = []
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# 5. MAIN AREA — TABS
# ═══════════════════════════════════════════════════════════════════════════════
st.title("⛅ WeatherGPT")
st.caption(
    "🤖 A rule-based conversational weather assistant | "
    "Data: [Open-Meteo](https://open-meteo.com/) (free, no API key) | "
    f"⏰ {datetime.datetime.now().strftime('%d %b %Y, %H:%M')}"
)

tab_chat, tab_current, tab_forecast, tab_alerts, tab_climate = st.tabs([
    "💬 Chat", "📊 Current Weather", "📅 7-Day Forecast",
    "⚠️ Alerts", "🌍 Climate Info",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: CHAT INTERFACE
# ─────────────────────────────────────────────────────────────────────────────
with tab_chat:
    st.subheader("💬 Chat with WeatherGPT")
    st.info(
        "💡 **How it works:** Type any weather question below. "
        "The app uses keyword matching to understand your question "
        "and real-time Open-Meteo API data to answer it. "
        "Make sure to enter a city in the sidebar first!",
        icon="ℹ️"
    )

    # Render all previous chat messages
    chat_container = st.container()
    with chat_container:
        if not st.session_state["chat_history"]:
            st.markdown(
                """
                <div class="bot-bubble">
                ⛅ <b>WeatherGPT</b> — Hello! I'm your weather assistant.<br><br>
                Enter a city in the sidebar and ask me anything about weather.
                Try: <i>"What is the temperature?"</i> or
                <i>"Will it rain tomorrow?"</i>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for msg in st.session_state["chat_history"]:
                render_chat_bubble(msg)

    st.divider()

    # ── Chat input row ───────────────────────────────────────────────────────
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_message = st.text_input(
            "Your message:",
            placeholder="e.g. 'Will it rain tomorrow?' or 'How humid is it?'",
            key="chat_input",
            label_visibility="collapsed",
        )
    with col_send:
        send_btn = st.button("Send ➤", use_container_width=True)

    if send_btn and user_message.strip():
        handle_user_message(user_message)
        # Clear the input by rerunning (Streamlit re-reads the widget fresh)
        st.rerun()

    # ── Suggested questions ──────────────────────────────────────────────────
    st.markdown("**💡 Try asking:**")
    suggestion_cols = st.columns(4)
    suggestions = [
        "What is the temperature?",
        "Will it rain today?",
        "Show the 7-day forecast",
        "Any weather alerts?",
        "How humid is it?",
        "What is the wind speed?",
        "What is the UV index?",
        "What is climate change?",
    ]
    for i, suggestion in enumerate(suggestions):
        with suggestion_cols[i % 4]:
            if st.button(suggestion, key=f"sug_{i}"):
                handle_user_message(suggestion)
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: CURRENT WEATHER DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tab_current:
    st.subheader("📊 Current Weather Dashboard")
    weather_data = st.session_state.get("weather_data")

    if not weather_data:
        st.info("👈 Enter a city name in the sidebar to see current weather data.")
    elif weather_data.get("error"):
        st.error(weather_data["error"])
    else:
        current  = weather_data["current"]
        location = weather_data["location"]

        st.markdown(
            f"### 📍 {location['name']}, {location['country']}  "
            f"— {current['description']}"
        )
        st.caption(f"Timezone: {location['timezone']}  |  "
                   f"Lat: {location['latitude']}°, Lon: {location['longitude']}°")

        # ── Key metrics row ──────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌡️ Temperature",  f"{current['temperature']}°C",
                  f"Feels {current['feels_like']}°C")
        c2.metric("💧 Humidity",     f"{current['humidity']}%")
        c3.metric("💨 Wind Speed",   f"{current['wind_speed']} km/h")
        c4.metric("☀️ UV Index",     current['uv_index'])

        st.divider()

        # ── Detail cards ─────────────────────────────────────────────────────
        d1, d2, d3 = st.columns(3)
        with d1:
            st.markdown("#### 🌡️ Temperature Details")
            st.markdown(f"- **Actual:** {current['temperature']}°C")
            st.markdown(f"- **Feels like:** {current['feels_like']}°C")
            day_night = "☀️ Daytime" if current['is_day'] else "🌙 Nighttime"
            st.markdown(f"- **Time of day:** {day_night}")

        with d2:
            st.markdown("#### 🌧️ Precipitation")
            st.markdown(f"- **Current rain:** {current['rain']} mm")
            st.markdown(f"- **Precipitation:** {current['precipitation']} mm")
            st.markdown(f"- **Humidity:** {current['humidity']}%")

        with d3:
            st.markdown("#### 💨 Wind")
            wind_dir_num = current.get("wind_direction", 0)
            compass_dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            compass = compass_dirs[round(wind_dir_num / 45) % 8]
            st.markdown(f"- **Speed:** {current['wind_speed']} km/h")
            st.markdown(f"- **Direction:** {compass} ({wind_dir_num}°)")
            st.markdown(f"- **UV Index:** {current['uv_index']}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: 7-DAY FORECAST
# ─────────────────────────────────────────────────────────────────────────────
with tab_forecast:
    st.subheader("📅 7-Day Weather Forecast")
    weather_data = st.session_state.get("weather_data")

    if not weather_data:
        st.info("👈 Enter a city name in the sidebar to see the forecast.")
    elif weather_data.get("error"):
        st.error(weather_data["error"])
    else:
        forecast = weather_data["forecast"]
        location = weather_data["location"]

        st.markdown(f"#### 📍 {location['name']}, {location['country']}")
        st.caption(
            "📌 Forecast data comes from Open-Meteo API. "
            "Accuracy is best for 1–3 days and decreases beyond that."
        )

        # ── Forecast cards ────────────────────────────────────────────────────
        cols = st.columns(7)
        for i, day in enumerate(forecast[:7]):
            with cols[i]:
                st.markdown(f"**{day['date']}**")
                # Get just the emoji from the description
                desc_parts = day['description'].split()
                emoji = desc_parts[0] if desc_parts else "🌡️"
                st.markdown(f"<div style='font-size:2em;text-align:center'>{emoji}</div>",
                            unsafe_allow_html=True)
                st.metric("Max", f"{day['temp_max']}°C")
                st.metric("Min", f"{day['temp_min']}°C")
                st.caption(f"🌧️ {day['rain_probability']}%")
                st.caption(f"💨 {day['wind_speed_max']} km/h")

        st.divider()

        # ── Temperature bar chart using Streamlit native ─────────────────────
        st.markdown("#### 📈 Temperature Range Chart")
        import pandas as pd

        chart_data = pd.DataFrame({
            "Date":    [d["date"] for d in forecast],
            "Max °C":  [d["temp_max"] for d in forecast],
            "Min °C":  [d["temp_min"] for d in forecast],
        }).set_index("Date")

        st.line_chart(chart_data)

        # ── Rain probability bar chart ────────────────────────────────────────
        st.markdown("#### ☔ Rain Probability (%)")
        rain_data = pd.DataFrame({
            "Date":              [d["date"] for d in forecast],
            "Rain Probability %": [d["rain_probability"] for d in forecast],
        }).set_index("Date")
        st.bar_chart(rain_data)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: ALERTS
# ─────────────────────────────────────────────────────────────────────────────
with tab_alerts:
    st.subheader("⚠️ Weather Alerts")
    weather_data = st.session_state.get("weather_data")

    if not weather_data:
        st.info("👈 Enter a city name in the sidebar to check weather alerts.")
    elif weather_data.get("error"):
        st.error(weather_data["error"])
    else:
        current  = weather_data["current"]
        forecast = weather_data["forecast"]
        location = weather_data["location"]

        alerts = check_alerts(current, forecast)
        summary = get_alert_summary(alerts)

        st.markdown(f"#### 📍 {location['name']}, {location['country']}")
        st.markdown(f"**Status:** {summary}")
        st.divider()

        if not alerts:
            st.success("✅ All conditions are within safe thresholds. Enjoy the weather!")
        else:
            for alert in alerts:
                severity = alert["severity"]
                css_class = f"alert-{severity}"
                st.markdown(
                    f'<div class="{css_class}">'
                    f'<strong>{alert["icon"]} {alert["title"]}</strong> '
                    f'<em>(Severity: {severity.upper()})</em><br>'
                    f'{alert["message"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.write("")  # spacer

        # ── Threshold explanation ────────────────────────────────────────────
        with st.expander("ℹ️ How are alerts generated? (click to expand)"):
            st.markdown("""
**Alert thresholds used in this project:**

| Condition | Threshold | Severity |
|---|---|---|
| Temperature | > 40°C | 🔴 Danger |
| Temperature | > 35°C | 🟠 Warning |
| Temperature | < 0°C | 🔴 Danger |
| Temperature | < 5°C | 🟠 Warning |
| Rain probability | > 80% | 🟠 Warning |
| Rain probability | > 50% | 🟡 Watch |
| Wind speed | > 60 km/h | 🔴 Danger |
| Wind speed | > 40 km/h | 🟠 Warning |
| UV index | > 10 | 🔴 Danger |
| UV index | > 7 | 🟠 Warning |
| Humidity | > 90% | 🟡 Watch |

These thresholds are stored as constants in `utils/alert_engine.py` and can be easily modified.
            """)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: CLIMATE INFORMATION
# ─────────────────────────────────────────────────────────────────────────────
with tab_climate:
    st.subheader("🌍 Climate Information")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🌤️ What is Weather?")
        st.markdown("""
Weather is the **short-term** state of the atmosphere at a specific
time and place. It can change from hour to hour or day to day.

**Weather includes:**
- Temperature (how hot or cold it is)
- Precipitation (rain, snow, hail)
- Wind speed and direction
- Humidity (moisture in the air)
- Cloudiness and visibility

**Example:** *"It is raining and 22°C in Mumbai today."*
        """)

    with col_b:
        st.markdown("### 🌏 What is Climate?")
        st.markdown("""
Climate is the **long-term pattern** of weather in a region,
typically averaged over **30 years** or more.

**Climate includes:**
- Average seasonal temperatures
- Typical rainfall patterns
- Prevailing wind patterns

**Example:** *"Mumbai has a tropical climate with heavy monsoon rains
from June to September."*
        """)

    st.divider()

    st.markdown("""
    > 🎙️ **Easy Memory Trick:**
    > *"Climate is what you **EXPECT**; weather is what you **GET**."*
    """)

    st.divider()

    st.markdown("### 🌡️ Climate Change")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("#### What is it?")
        st.markdown(
            "Long-term shift in global temperatures and weather patterns, "
            "primarily caused by human activities like burning fossil fuels "
            "since the Industrial Revolution (~1850)."
        )
    with cols[1]:
        st.markdown("#### Key Facts")
        st.markdown("""
- 🌡️ Global average temperature has risen **~1.1°C** since pre-industrial times
- 🧊 Arctic sea ice shrinks at **~13% per decade**
- 🌊 Sea levels rise at **~3.3 mm/year**
- 🌲 Extreme weather events are becoming more frequent
        """)
    with cols[2]:
        st.markdown("#### What can we do?")
        st.markdown("""
- 🌱 Use renewable energy
- 🚌 Use public transport
- 🌳 Plant trees
- 💡 Reduce electricity waste
- ♻️ Recycle and reduce waste
        """)

    st.divider()

    st.markdown("### 🌏 Major Climate Zones of the World")
    st.markdown("""
| Climate Zone | Characteristics | Example Regions |
|---|---|---|
| 🌴 Tropical | Hot all year, heavy rainfall | Amazon, Central Africa, South India |
| 🏜️ Arid/Desert | Very dry, extreme temperature swings | Sahara, Rajasthan, Arabian Peninsula |
| 🌿 Temperate | Mild seasons, moderate rainfall | Western Europe, Eastern USA |
| 🌨️ Continental | Hot summers, very cold winters | Russia, Central Canada |
| ❄️ Polar | Extremely cold, little precipitation | Arctic, Antarctica |
| ⛰️ Highland | Varies with altitude | Himalayas, Andes, Alps |
    """)

    st.caption(
        "📚 Data source: IPCC Reports | "
        "WMO (World Meteorological Organization)"
    )
