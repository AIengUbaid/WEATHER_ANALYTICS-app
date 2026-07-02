from dotenv import load_dotenv
import os
import streamlit as st
import requests
import pandas as pd

load_dotenv()

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
if API_KEY:
    API_KEY = API_KEY.strip()

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
CITIES = ["Mumbai", "Delhi", "Bangalore", "London", "New York", "Tokyo"]
REQUEST_TIMEOUT = 10  

class AuthError(Exception):
    
    pass

def fetch_weather(city: str, api_key: str) -> dict | None:
    try:
        response = requests.get(
            BASE_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()   
        
        
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Response root is not a JSON object.")
            
        return {
            "City": city,
            "Temperature (°C)": data["main"]["temp"],
            "Feels Like (°C)": data["main"]["feels_like"],
            "Humidity (%)": data["main"]["humidity"],
            "Wind Speed (m/s)": data["wind"]["speed"],
            "Condition": data["weather"][0]["main"],
            "Description": data["weather"][0]["description"].capitalize(),
        }

    except requests.exceptions.ConnectionError:
        st.warning(f"⚠️ {city}: Could not reach the weather server. Check your internet connection.")
        return None
    except requests.exceptions.Timeout:
        st.warning(f"⚠️ {city}: Request timed out after {REQUEST_TIMEOUT} s.")
        return None
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        if status == 401:
            raise AuthError()           
        elif status == 404:
            st.warning(f"⚠️ {city}: City not found by the API.")
        elif status == 429:
            st.warning(f"⚠️ {city}: Rate limit exceeded. Wait a moment and try again.")
        else:
            st.warning(f"⚠️ {city}: HTTP {status} error.")
        return None
    except requests.exceptions.RequestException as exc:
        st.warning(f"⚠️ {city}: Unexpected network error — {exc}")
        return None
    except (KeyError, IndexError, ValueError, TypeError) as exc:
        st.warning(f"⚠️ {city}: Unexpected API response format — {exc}")
        return None


st.title("🌤️ Real-Time Multi-City Weather Analytics")
st.write("This app integrates a live weather API with Pandas to structure real-time data.")

if not API_KEY:
    st.error(
        "🔑 No API key found. "
        "Set OPENWEATHERMAP_API_KEY in your .env file or as an environment variable."
    )
    st.stop()

if st.button("Fetch Live Analytics"):
    weather_data_list: list[dict] = []
    failed_cities: list[str] = []

    with st.spinner("Connecting to weather servers…"):
        try:
            for city in CITIES:
                metrics = fetch_weather(city, API_KEY)
                if metrics:
                    weather_data_list.append(metrics)
                else:
                    failed_cities.append(city)
        except AuthError:
            st.error(
                "🔑 Invalid API key — all requests aborted. "
                "Please check OPENWEATHERMAP_API_KEY in your .env file."
            )
            st.stop()

    if weather_data_list:
        df = pd.DataFrame(weather_data_list).set_index("City")

        st.subheader("📊 Key Market Insights")
        col1, col2, col3 = st.columns(3)

        hottest_city = df["Temperature (°C)"].idxmax()
        hottest_temp = df["Temperature (°C)"].max()
        col1.metric("🔥 Hottest City", f"{hottest_city}", f"{hottest_temp:.1f}°C")

        coldest_city = df["Temperature (°C)"].idxmin()
        coldest_temp = df["Temperature (°C)"].min()
        col2.metric("🧊 Coldest City", f"{coldest_city}", f"{coldest_temp:.1f}°C")

        most_humid_city = df["Humidity (%)"].idxmax()
        most_humid = df["Humidity (%)"].max()
        col3.metric("💧 Most Humid", f"{most_humid_city}", f"{most_humid}%")

        st.subheader("📋 Live Structured Weather Database")
        st.dataframe(df, use_container_width=True)

        st.subheader("📈 Temperature Comparison")
        st.bar_chart(df["Temperature (°C)"])

        st.subheader("💧 Humidity Comparison")
        st.bar_chart(df["Humidity (%)"])
        
        if failed_cities:
            st.info(
                f"Data could not be retrieved for: **{', '.join(failed_cities)}**. "
                "See warnings above for details."
            )
    else:
        st.error(
            "❌ No data could be retrieved for any city. "
            "Please check your API key and internet connection."
        )

