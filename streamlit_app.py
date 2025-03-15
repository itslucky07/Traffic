import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

st.set_page_config(page_title="India Traffic Monitor", layout="wide")

st.title("🚦 Live Traffic Monitoring in India 🇮🇳")

def get_osm_traffic_data(location):
    geolocator = Nominatim(user_agent="geoapi")
    location_data = geolocator.geocode(location + ", India")
    
    if not location_data:
        return "⚠️ Location not found. Try another one."

    lat, lon = location_data.latitude, location_data.longitude
    traffic_url = f"https://api.openstreetmap.org/api/0.6/map?bbox={lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}"
    response = requests.get(traffic_url)

    if response.status_code == 200:
        return f"🚦 Live traffic data available at {location}, India."
    else:
        return "⚠️ No traffic data found for this location."

def show_traffic_map(location):
    geolocator = Nominatim(user_agent="geoapi")
    location_data = geolocator.geocode(location + ", India")

    if location_data:
        lat, lon = location_data.latitude, location_data.longitude
        traffic_map = folium.Map(location=[lat, lon], zoom_start=13)
        folium.Marker([lat, lon], popup="Traffic Location", icon=folium.Icon(color="red")).add_to(traffic_map)
        return traffic_map
    else:
        return "⚠️ Invalid location."

location = st.text_input("Enter an Indian city (e.g., Delhi, Mumbai, Bangalore)")

if location:
    st.subheader("Traffic Data Status:")
    traffic_info = get_osm_traffic_data(location)
    st.write(traffic_info)

    st.subheader("Live Traffic Map:")
    map_output = show_traffic_map(location)
    folium_static(map_output)
