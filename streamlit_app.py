import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import requests

# 🚦 TomTom API Key (Replace with your actual API key)
TOMTOM_API_KEY = "shXffocf9KYkZVUQviB8JYApUg0NSVoG"

# Set Page Title
st.set_page_config(page_title="🚦 Live Traffic & Route Finder", layout="wide")
st.title("🚦 India Live Traffic & Route Finder")

# Sidebar User Inputs
st.sidebar.header("📍 Enter Locations")
current_location = st.sidebar.text_input("Your Current Location", placeholder="e.g., Connaught Place, Delhi")
destination = st.sidebar.text_input("Destination", placeholder="e.g., India Gate, Delhi")

# Get Latitude & Longitude
def get_lat_lon(location):
    geolocator = Nominatim(user_agent="geoapi", timeout=10)
    location_data = geolocator.geocode(location + ", India")
    return (location_data.latitude, location_data.longitude) if location_data else (None, None)

# Fetch Real-Time Traffic from TomTom API
def get_traffic_status(lat, lon):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={TOMTOM_API_KEY}"
    response = requests.get(url).json()
    
    if "flowSegmentData" in response:
        return response["flowSegmentData"]["currentSpeed"], response["flowSegmentData"]["freeFlowSpeed"]
    return None, None

# Fetch Route from TomTom API
def get_route(start_lat, start_lon, end_lat, end_lon):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json?key={TOMTOM_API_KEY}"
    response = requests.get(url).json()
    
    if "routes" in response:
        return response["routes"][0]["legs"][0]["points"]
    return None

# Display Traffic & Route Map
def show_traffic_map():
    start = get_lat_lon(current_location)
    end = get_lat_lon(destination)

    if not start[0] or not end[0]:
        return "⚠️ Invalid locations. Please check your input."

    m = folium.Map(location=start, zoom_start=12)

    # Get Traffic Data for Start & Destination
    start_speed, start_free_flow = get_traffic_status(*start)
    end_speed, end_free_flow = get_traffic_status(*end)

    # Determine Traffic Conditions
    def traffic_color(speed, free_flow):
        if speed >= free_flow * 0.8:
            return "green"
        elif speed >= free_flow * 0.5:
            return "orange"
        return "red"

    start_color = traffic_color(start_speed, start_free_flow)
    end_color = traffic_color(end_speed, end_free_flow)

    # Add Markers for Start & Destination
    folium.Marker(start, popup="🚗 Start", icon=folium.Icon(color=start_color)).add_to(m)
    folium.Marker(end, popup="🏁 Destination", icon=folium.Icon(color=end_color)).add_to(m)

    # Get Route & Draw on Map
    route_points = get_route(*start, *end)
    if route_points:
        folium.PolyLine(locations=[(p["latitude"], p["longitude"]) for p in route_points], color="blue", weight=6).add_to(m)

    return m

# Display Results
if current_location and destination:
    folium_static(show_traffic_map())
