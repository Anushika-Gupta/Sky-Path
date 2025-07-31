import folium

# Dummy coordinates (update these)
airport_coords = {
    "A": (28.6139, 77.2090),   # Delhi
    "B": (19.0760, 72.8777),   # Mumbai
    "C": (12.9716, 77.5946),   # Bangalore
    "D": (13.0827, 80.2707),   # Chennai
    "E": (22.5726, 88.3639),   # Kolkata
}

def plot_geo_path(path):
    m = folium.Map(location=[23.5, 80.5], zoom_start=5)

    # Add markers
    for code, coord in airport_coords.items():
        folium.Marker(coord, tooltip=code, icon=folium.Icon(color='blue')).add_to(m)

    # Highlight path
    path_coords = [airport_coords[flight.origin.name] for flight in path]
    path_coords.append(airport_coords[path[-1].dest.name])

    folium.PolyLine(path_coords, color="green", weight=4.5, opacity=0.8).add_to(m)

    # Save
    m.save("flight_path_map.html")
    print("🗺️ Map saved as flight_path_map.html")
