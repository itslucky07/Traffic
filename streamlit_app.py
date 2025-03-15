import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests

TOMTOM_API_KEY = "shXffocf9KYkZVUQviB8JYApUg0NSVoG"


st.set_page_config(page_title="🚦 Traffic & Route Finder", layout="wide")

st.title("🚦 Live Traffic & Route Finder")

current_location = st.sidebar.text_input("📍 Current Location", placeholder="e.g., Delhi")
destination = st.sidebar.text_input("🎯 Destination", placeholder="e.g., Mumbai")

def get_lat_lon(location):
    geolocator = Nominatim(user_agent="geoapi", timeout=10)
    location_data = geolocator.geocode(location + ", India")
    return (location_data.latitude, location_data.longitude) if location_data else (None, None)

def get_route_data(start_lat, start_lon, end_lat, end_lon, avoid_traffic=False):
    avoid_param = "&avoid=traffic" if avoid_traffic else ""
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json?key={TOMTOM_API_KEY}{avoid_param}"
    response = requests.get(url).json()
    
    if "routes" in response:
        route = response["routes"][0]["legs"][0]
        return route["points"], route["summary"]["lengthInMeters"] / 1000, route["summary"]["travelTimeInSeconds"] / 3600
    return None, None, None

def show_map():
    start = get_lat_lon(current_location)
    end = get_lat_lon(destination)
    if not start[0] or not end[0]:
        return folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    m = folium.Map(location=start, zoom_start=12)
    folium.Marker(start, popup="Start", icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker(end, popup="Destination", icon=folium.Icon(color="red")).add_to(m)
    return m

if current_location and destination:
    st_folium(show_map(), width=1000, height=600)
