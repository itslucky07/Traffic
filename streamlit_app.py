import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests

# 🗺️ TomTom API Key (Replace with your valid API Key)
TOMTOM_API_KEY = "QSX465abuQsJUJEWPdBZ8S4K0ZrqsqQ7"

st.set_page_config(page_title="🚦 India Live Traffic & Route", layout="wide")
st.title("🚦 Live Traffic & Route Finder for India 🇮🇳")

# Sidebar Inputs
st.sidebar.header("📍 Enter Locations")
current_location = st.sidebar.text_input("Your Current Location", placeholder="e.g., Connaught Place, Delhi")
destination = st.sidebar.text_input("Destination", placeholder="e.g., India Gate, Delhi")

# Function to get latitude and longitude
def get_lat_lon(location):
    geolocator = Nominatim(user_agent="geoapi", timeout=10)
    location_data = geolocator.geocode(location + ", India")
    return (location_data.latitude, location_data.longitude) if location_data else (None, None)

# Function to fetch traffic status for a point
def get_traffic_status(lat, lon):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={TOMTOM_API_KEY}"
    response = requests.get(url).json()
    if "flowSegmentData" in response:
        speed = response["flowSegmentData"]["currentSpeed"]
        free_flow = response["flowSegmentData"]["freeFlowSpeed"]
        return speed, free_flow
    return None, None

# Function to determine traffic color
def traffic_color(speed, free_flow):
    if not speed or not free_flow:
        return "gray"
    if speed >= free_flow * 0.8:
        return "blue"  # No Traffic
    elif speed >= free_flow * 0.5:
        return "orange"  # Moderate Traffic
    return "red"  # Heavy Traffic

# Function to get route data
def get_route(start_lat, start_lon, end_lat, end_lon):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json?key={TOMTOM_API_KEY}"
    response = requests.get(url).json()
    
    if "routes" in response:
        route_points = response["routes"][0]["legs"][0]["points"]
        return route_points
    return None

# Function to generate the map with traffic colors
def show_traffic_map():
    start = get_lat_lon(current_location)
    end = get_lat_lon(destination)

    if not start[0] or not end[0]:
        st.error("⚠️ Invalid locations. Please check your input.")
        return folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Default map of India

    m = folium.Map(location=start, zoom_start=12)

    # Get Route
    route = get_route(*start, *end)

    if route:
        for i in range(len(route) - 1):
            lat1, lon1 = route[i]["latitude"], route[i]["longitude"]
            lat2, lon2 = route[i + 1]["latitude"], route[i + 1]["longitude"]

            # Fetch traffic for this segment
            speed, free_flow = get_traffic_status(lat1, lon1)
            color = traffic_color(speed, free_flow)

            # Draw segment with traffic color
            folium.PolyLine([(lat1, lon1), (lat2, lon2)], color=color, weight=6).add_to(m)

    return m

# Show Map in Streamlit
if current_location and destination:
    st_folium(show_traffic_map(), width=1200, height=600)
