import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

# Set your TomTom API key here
TOMTOM_API_KEY = "shXffocf9KYkZVUQviB8JYApUg0NSVoG"


# Function to get route data from TomTom
def get_route(start_lat, start_lon, end_lat, end_lon):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json?key={TOMTOM_API_KEY}&traffic=true"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]
            points = route["legs"][0]["points"]
            traffic_data = route.get("summary", {})
            return points, traffic_data
        else:
            st.error("No routes found! Please check your locations.")
            return None, None

    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None, None

# Function to get live traffic conditions
def get_traffic_info(start_lat, start_lon, end_lat, end_lon):
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={start_lat},{start_lon}&key={TOMTOM_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "flowSegmentData" in data:
            return data["flowSegmentData"]
        else:
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Traffic API Error: {e}")
        return None

# Function to generate map with traffic conditions
def show_traffic_map(start_lat, start_lon, end_lat, end_lon):
    points, traffic_data = get_route(start_lat, start_lon, end_lat, end_lon)

    if not points:
        return None

    # Create map centered at the start location
    m = folium.Map(location=[start_lat, start_lon], zoom_start=12)

    # Traffic colors based on speed ratio
    traffic_color = {"HEAVY": "red", "MODERATE": "orange", "FREE_FLOW": "blue"}

    # Plot route with traffic conditions
    for i in range(len(points) - 1):
        segment_start = points[i]
        segment_end = points[i + 1]

        # Fetch traffic info for each segment
        traffic_info = get_traffic_info(segment_start["latitude"], segment_start["longitude"], end_lat, end_lon)
        if traffic_info:
            status = traffic_info["currentSpeed"]
            free_flow_speed = traffic_info["freeFlowSpeed"]
            speed_ratio = status / free_flow_speed if free_flow_speed else 1

            # Define traffic conditions
            if speed_ratio < 0.4:
                color = "red"  # Heavy traffic
            elif speed_ratio < 0.7:
                color = "orange"  # Moderate traffic
            else:
                color = "blue"  # Free flow
        else:
            color = "blue"  # Default color if no traffic info

        # Add polyline to map
        folium.PolyLine(
            [(segment_start["latitude"], segment_start["longitude"]),
             (segment_end["latitude"], segment_end["longitude"])],
            color=color,
            weight=6,
            opacity=0.7
        ).add_to(m)

    # Add start and end markers
    folium.Marker([start_lat, start_lon], popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker([end_lat, end_lon], popup="Destination", icon=folium.Icon(color="blue")).add_to(m)

    return m

# Streamlit App UI
st.title("🚗 Live Traffic Route Finder")
st.markdown("Find the best route with live traffic conditions in India!")

# User inputs
start_location = st.text_input("Enter Start Location (e.g., Mumbai)")
destination = st.text_input("Enter Destination (e.g., Pune)")

if st.button("Find Route"):
    if start_location and destination:
        # Get coordinates from TomTom geocoding API
        def get_coordinates(location):
            geo_url = f"https://api.tomtom.com/search/2/geocode/{location}.json?key={TOMTOM_API_KEY}"
            try:
                response = requests.get(geo_url)
                response.raise_for_status()
                geo_data = response.json()
                if "results" in geo_data and len(geo_data["results"]) > 0:
                    return geo_data["results"][0]["position"]["lat"], geo_data["results"][0]["position"]["lon"]
                else:
                    return None, None
            except:
                return None, None

        start_lat, start_lon = get_coordinates(start_location)
        end_lat, end_lon = get_coordinates(destination)

        if start_lat and end_lat:
            map_display = show_traffic_map(start_lat, start_lon, end_lat, end_lon)
            if map_display:
                st_folium(map_display, width=800, height=500)
        else:
            st.error("Invalid location entered. Please try again.")

