app_code = """ 
import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import requests

st.set_page_config(page_title="🚦 India Traffic Live", layout="wide")

st.title("🚦 Live Traffic Monitoring for India 🇮🇳")

def get_lat_lon(location):
    geolocator = Nominatim(user_agent="geoapi")
    location_data = geolocator.geocode(location + ", India")
    
    if location_data:
        return location_data.latitude, location_data.longitude
    return None, None

def fetch_traffic_data(lat, lon):
    # Dummy simulation for traffic levels (Replace with real API like TomTom, OpenTraffic, or Mapbox)
    import random
    traffic_levels = ["Low", "Medium", "High"]
    return random.choice(traffic_levels)

def get_color(traffic_level):
    return {
        "Low": "green",
        "Medium": "orange",
        "High": "red"
    }.get(traffic_level, "gray")

def show_traffic_map(location):
    lat, lon = get_lat_lon(location)

    if not lat or not lon:
        return "⚠️ Invalid location."

    # Create map
    traffic_map = folium.Map(location=[lat, lon], zoom_start=13)

    # Simulating 5 nearby roads with random traffic data
    for i in range(5):
        road_lat = lat + (i * 0.002)
        road_lon = lon + (i * 0.002)
        traffic_status = fetch_traffic_data(road_lat, road_lon)
        color = get_color(traffic_status)

        folium.Marker(
            [road_lat, road_lon], 
            popup=f"Traffic: {traffic_status}", 
            icon=folium.Icon(color=color)
        ).add_to(traffic_map)

    return traffic_map

# User Input
location = st.text_input("Enter an Indian city (e.g., Delhi, Mumbai, Bangalore)")

if location:
    st.subheader("🚥 Live Traffic Data")
    traffic_map = show_traffic_map(location)
    folium_static(traffic_map)
"""

# Save to Google Drive
with open("/content/drive/MyDrive/app.py", "w") as file:
    file.write(app_code)
