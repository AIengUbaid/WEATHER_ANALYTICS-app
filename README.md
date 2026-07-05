Real-Time Multi-City Weather Analytics

A live weather dashboard built with Python and Streamlit that fetches real-time weather data for multiple cities using the OpenWeatherMap API.

Features:
Live temperature, humidity, wind speed and weather conditions
Automatic data structuring with Pandas
Visual comparisons with bar charts
Hottest, coldest and most humid city insights
Robust error handling for API failures and network issues

Technologies Used:
Python, Streamlit, Pandas, Requests
OpenWeatherMap API
Environment variables for secure API key management

How to Run:
Clone the repo
Install requirements: pip install streamlit pandas requests python-dotenv
Add your OpenWeatherMap API key to a .env file as OPENWEATHERMAP_API_KEY=your_key
Run: streamlit run weather_pre.py
