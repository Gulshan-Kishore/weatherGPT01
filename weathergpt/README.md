# ⛅ WeatherGPT
### Conversational AI for Weather Forecasting, Alerts, and Climate Information
#### A Beginner-Friendly B.Tech CSE AI & ML College Project

---

> **Honest disclaimer:** WeatherGPT is NOT a trained generative AI model.
> It uses **real-time weather data** from the Open-Meteo API and **rule-based
> keyword matching** to understand and answer your questions.
> This approach is simple, transparent, and perfect for a college project!

---

## 📁 Project Structure

```
weathergpt/
│
├── app.py                    ← Main Streamlit application (run this)
│
├── utils/
│   ├── __init__.py           ← Makes 'utils' a Python package
│   ├── weather_api.py        ← Fetches data from Open-Meteo API
│   ├── intent_detector.py    ← Keyword-based intent classification
│   ├── alert_engine.py       ← Threshold-based weather alerts
│   └── response_builder.py  ← Generates natural-language responses
│
├── requirements.txt          ← Python dependencies
├── test_weathergpt.py        ← Test script (run to verify everything works)
└── README.md                 ← This file
```

---

## 🚀 Installation (Mac — Step by Step)

### Step 1: Make sure Python is installed
```bash
python3 --version
# Should print Python 3.8 or higher
```

### Step 2: Navigate to the project folder
```bash
cd /path/to/weather/weathergpt
# Example: cd ~/Documents/weather/weathergpt
```

### Step 3: (Optional but recommended) Create a virtual environment
A virtual environment keeps this project's packages separate from other projects.
```bash
python3 -m venv venv          # Creates a folder called 'venv'
source venv/bin/activate      # Activates it (your terminal shows "(venv)")
```

### Step 4: Install dependencies
```bash
pip install -r requirements.txt
```
This installs only 3 libraries:
- **streamlit** — creates the web app UI
- **requests** — sends HTTP requests to the weather API
- **pandas** — handles data for the forecast charts

### Step 5: Run the app
```bash
streamlit run app.py
```
Your browser will automatically open at **http://localhost:8501**

### Step 6: (Optional) Run the tests first
```bash
python test_weathergpt.py
```

---

## 🌐 APIs Used

| API | Purpose | Cost | API Key? |
|-----|---------|------|----------|
| [Open-Meteo Weather API](https://api.open-meteo.com) | Current weather + 7-day forecast | FREE | ❌ None needed |
| [Open-Meteo Geocoding API](https://geocoding-api.open-meteo.com) | City name → Latitude/Longitude | FREE | ❌ None needed |

---

## 💬 How to Use the App

1. **Enter a city** in the left sidebar (e.g., Mumbai, Delhi, London)
2. Click **"🔍 Get Weather"** or use a **Quick City** button
3. Go to the **💬 Chat** tab and ask questions like:
   - *"What is the temperature?"*
   - *"Will it rain today?"*
   - *"Show me the 7-day forecast"*
   - *"Are there any weather alerts?"*
   - *"What is the UV index?"*
   - *"What is climate change?"*
4. Explore the other tabs for detailed weather data

---

## 🏗️ How the System Works — Simple Explanation

```
User types question
        ↓
[Intent Detector]  ← Keyword matching (if/elif)
  "Will it rain?"  →  intent = "rain"
        ↓
[Weather API]  ← Fetches live data from Open-Meteo
  Returns temperature, humidity, rain probability, etc.
        ↓
[Response Builder]  ← Picks the right template for the intent
  Fills in actual numbers from the API
        ↓
[Alert Engine]  ← Checks values against thresholds
  temp > 40°C → "Extreme Heat" danger alert
        ↓
Chat bubble displayed to user
```

---

## 🧠 Algorithms Used

### 1. Rule-Based Intent Detection (in `intent_detector.py`)
```python
msg = user_message.lower()  # Step 1: lowercase

if any(word in msg for word in ["rain", "umbrella", "shower"]):
    return "rain"            # Step 2: keyword match
elif any(word in msg for word in ["temperature", "hot", "cold"]):
    return "temperature"
# ... and so on
```
**Why this approach?** Simple, transparent, no training data needed.

### 2. Threshold-Based Alert System (in `alert_engine.py`)
```python
if temperature > 40:     # Danger threshold
    generate_danger_alert()
elif temperature > 35:   # Warning threshold
    generate_warning_alert()
```
**Why this approach?** Easy to understand, tune, and explain.

### 3. REST API Communication (in `weather_api.py`)
```python
response = requests.get(url, params=params)  # Like opening a URL
data = response.json()                        # Parse the JSON response
```
**Why Open-Meteo?** Free, no API key, accurate, well-documented.

---

## 🔍 Testing Examples

| Question | Expected Intent | Expected Response |
|----------|----------------|-------------------|
| "What is the temperature?" | temperature | Shows °C, feels-like, condition |
| "Will it rain today?" | rain | Shows rain probability, umbrella advice |
| "How humid is it?" | humidity | Shows % humidity with comfort description |
| "Show the 7-day forecast" | forecast | Shows 7-day table |
| "Any weather alerts?" | alerts | Lists active alerts or "all safe" |
| "What is the UV index?" | uv_index | Shows UV number with risk level |
| "What is climate change?" | climate_info | Shows educational content |
| "hello" | greeting | Shows welcome message |
| "help" | help | Shows usage instructions |
| "xyzinvalidquestion" | unknown | Shows fallback with suggestions |

---

## ⚠️ Limitations

1. **Not a real AI model** — responses are template-based, not generative
2. **English only** — keyword matching works only in English
3. **Needs internet** — fetches live data; does not work offline
4. **No personal memory** — does not remember previous conversations
5. **Forecast accuracy** — Open-Meteo forecasts are less accurate beyond 3 days
6. **Keyword limitations** — very unusual phrasings may not be detected correctly
7. **Single language** — English only for intent detection

---

## 🔮 Future Improvements

1. **Add a real NLP model** — use spaCy or a fine-tuned BERT for intent detection
2. **Historical weather data** — show past weather trends using Open-Meteo historical API
3. **User location detection** — auto-detect city using IP geolocation
4. **Notifications** — email/SMS alerts when rain is forecasted
5. **Multi-language support** — add Hindi, Tamil, etc.
6. **Voice input** — use `speech_recognition` library for voice queries
7. **Weather map** — embed an interactive map with Folium

---

## 👨‍💻 Tech Stack

| Technology | Role |
|-----------|------|
| Python 3.8+ | Programming language |
| Streamlit | Web app framework |
| Requests | HTTP API communication |
| Pandas | Data manipulation for charts |
| Open-Meteo API | Free weather data source |

---

## 📚 References

- [Open-Meteo Documentation](https://open-meteo.com/en/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [WMO Weather Code Standard](https://open-meteo.com/en/docs#weathervariables)
- [IPCC Climate Reports](https://www.ipcc.ch/reports/)
- [Python Requests Library](https://requests.readthedocs.io/)
