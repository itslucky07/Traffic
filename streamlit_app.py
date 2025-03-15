import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import requests
from math import radians, cos, sin, asin, sqrt

# 🚦 TomTom API Key (Replace with your actual API key)
TOMTOM_API_KEY = "shXffocf9KYkZVUQviB8JYApUg0NSVoG"

# Set Page Title
st.set_page_config(page_title="🚦 India Live Traffic & Route Finder", layout="wide")
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
        route = response["routes"][0]["legs"][0]
        return route["points"], route["summary"]["lengthInMeters"], route["summary"]["travelTimeInSeconds"]
    return None, None, None

# Suggest Alternative Route (Less Traffic)
def get_alternate_route(start_lat, start_lon, end_lat, end_lon):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json?avoid=traffic&key={TOMTOM_API_KEY}"
    response = requests.get(url).json()
    
    if "routes" in response:
        route = response["routes"][0]["legs"][0]
        return route["points"], route["summary"]["lengthInMeters"], route["summary"]["travelTimeInSeconds"]
    return None, None, None

# Haversine Formula to Calculate Distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in KM
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# Traffic Color Code
def traffic_color(speed, free_flow):
    if not speed or not free_flow:
        return "gray"
    if speed >= free_flow * 0.8:
        return "blue"  # No Traffic
    elif speed >= free_flow * 0.5:
        return "orange"  # Moderate Traffic
    return "red"  # Heavy Traffic

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

    start_color = traffic_color(start_speed, start_free_flow)
    end_color = traffic_color(end_speed, end_free_flow)

    # Add Markers for Start & Destination
    folium.Marker(start, popup="🚗 Start", icon=folium.Icon(color=start_color)).add_to(m)
    folium.Marker(end, popup="🏁 Destination", icon=folium.Icon(color=end_color)).add_to(m)

    # Get Main Route & Alternative Route
    main_route, main_distance, main_time = get_route(*start, *end)
    alt_route, alt_distance, alt_time = get_alternate_route(*start, *end)

    # Draw Main Route in Blue
    if main_route:
        folium.PolyLine(locations=[(p["latitude"], p["longitude"]) for p in main_route], color="blue", weight=6, tooltip="Main Route").add_to(m)

    # Draw Alternative Route in Green
    if alt_route:
        folium.PolyLine(locations=[(p["latitude"], p["longitude"]) for p in alt_route], color="green", weight=6, tooltip="Alternative Route").add_to(m)

    # Show Distance & Time
    if main_distance and main_time:
        st.sidebar.markdown(f"🚗 **Main Route:** {main_distance/1000:.2f} km, ⏳ {main_time//60} min")
    if alt_distance and alt_time:
        st.sidebar.markdown(f"🛣️ **Alternative Route:** {alt_distance/1000:.2f} km, ⏳ {alt_time//60} min (Less Traffic)")

    return m

# Display Results
if current_location and destination:
    folium_static(show_traffic_map())
