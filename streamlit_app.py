import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import requests

# 🗺️ TomTom API Key (Replace with your valid API Key)
TOMTOM_API_KEY = "shXffocf9KYkZVUQviB8JYApUg0NSVoG"

st.set_page_config(page_title="🚦 India Traffic & Route Finder", layout="wide")

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

# Function to fetch traffic data
def get_traffic_status(lat, lon):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={TOMTOM_API_KEY}"
    response = requests.get(url).json()
    if "flowSegmentData" in response:
        return response["flowSegmentData"]["currentSpeed"], response["flowSegmentData"]["freeFlowSpeed"]
    return None, None

# Function to get route data
def get_route(start_lat, start_lon, end_lat, end_lon, avoid_traffic=False):
    avoid_param = "&avoid=traffic" if avoid_traffic else ""
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json?key={TOMTOM_API_KEY}{avoid_param}"
    response = requests.get(url).json()
    
    if "routes" in response:
        route = response["routes"][0]["legs"][0]
        return route["points"], route["summary"]["lengthInMeters"] / 1000, route["summary"]["travelTimeInSeconds"] / 3600
    return None, None, None

# Function to determine traffic color
def traffic_color(speed, free_flow):
    if not speed or not free_flow:
        return "gray"
    if speed >= free_flow * 0.8:
        return "blue"  # No Traffic
    elif speed >= free_flow * 0.5:
        return "orange"  # Moderate Traffic
    return "red"  # Heavy Traffic

# Function to generate the map
def show_traffic_map():
    start = get_lat_lon(current_location)
    end = get_lat_lon(destination)

    if not start[0] or not end[0]:
        st.error("⚠️ Invalid locations. Please check your input.")
        return folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Default map of India

    m = folium.Map(location=start, zoom_start=12)

    # Get Traffic Data
    start_speed, start_free_flow = get_traffic_status(*start)
    end_speed, end_free_flow = get_traffic_status(*end)

    start_color = traffic_color(start_speed, start_free_flow)
    end_color = traffic_color(end_speed, end_free_flow)

    # Add Markers
    folium.Marker(start, popup="🚗 Start", icon=folium.Icon(color=start_color)).add_to(m)
    folium.Marker(end, popup="🏁 Destination", icon=folium.Icon(color=end_color)).add_to(m)

    # Get Main & Alternative Route
    main_route, main_distance, main_time = get_route(*start, *end)
    alt_route, alt_distance, alt_time = get_route(*start, *end, avoid_traffic=True)

    # Draw Main Route in Red/Blue based on Traffic
    if main_route:
        route_color = "red" if start_color == "red" or end_color == "red" else "blue"
        folium.PolyLine([(p["latitude"], p["longitude"]) for p in main_route], color=route_color, weight=6, tooltip="Main Route").add_to(m)

    # Draw Alternative Route in Green
    if alt_route:
        folium.PolyLine([(p["latitude"], p["longitude"]) for p in alt_route], color="green", weight=6, tooltip="Alternative Route (Less Traffic)").add_to(m)

    # Display Distance & Time
    if main_distance and alt_distance:
        st.markdown("### 📏 Distance & ETA")
        st.write(f"🛑 **Main Route:** {main_distance:.2f} km | ⏳ {main_time:.2f} hrs")
        st.write(f"🟢 **Alternative Route:** {alt_distance:.2f} km | ⏳ {alt_time:.2f} hrs (Recommended)")

    return m

# Show Map in Streamlit
if current_location and destination:
    st_folium(show_traffic_map(), width=1200, height=600)
