from flight import Flight, Vertex, Graph as FlightGraph, FlightAgency
from graph import Graph as SimpleGraph
from visualize import visualize_graph
from geo_visualize import plot_geo_path
from auth import login, register
from database import get_db_path
from database import init_db
from colorama import Fore, init
import sqlite3
import joblib
import pandas as pd

init(autoreset=True)

# Load ML model
model = joblib.load("delay_model.pkl")
le_origin, le_dest, le_day, le_weather = joblib.load("label_encoders.pkl")

airport_day = {"A": "Mon", "B": "Tue", "C": "Wed", "D": "Thu", "E": "Fri"}
airport_weather = {"A": "Clear", "B": "Rain", "C": "Clear", "D": "Fog", "E": "Storm"}

# Predict delay
def predict_delay(flight):
    day = airport_day.get(flight.origin.name, "Tue")
    weather = airport_weather.get(flight.origin.name, "Clear")
    try:
        features = pd.DataFrame([{
            'origin': le_origin.transform([flight.origin.name])[0],
            'dest': le_dest.transform([flight.dest.name])[0],
            'departT': flight.departT,
            'day': le_day.transform([day])[0],
            'weather': le_weather.transform([weather])[0]
        }])
        return model.predict(features)[0]
    except Exception as e:
        print(Fore.RED + f"Prediction error: {e}")
        return 0

# Save trip to database
def save_trip(user_id, start, end, start_time, path, arrival_time, delay):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    itinerary_str = " → ".join([f.origin.name for f in path] + [path[-1].dest.name])
    cursor.execute("""
        INSERT INTO trips (user_id, start, end, start_time, itinerary, arrival_time, delay_minutes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, start, end, start_time, itinerary_str, f"{arrival_time}:00", int(delay)))
    conn.commit()
    conn.close()

# Show user past trips
def show_past_trips(user_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT start, end, start_time, itinerary, arrival_time, delay_minutes FROM trips WHERE user_id = ?", (user_id,))
    trips = cursor.fetchall()
    if not trips:
        print(Fore.YELLOW + "No saved itineraries.")
    else:
        print(Fore.CYAN + "\n🧳 Your Saved Trips:")
        for t in trips:
            print(f"🔸 {t[0]} → {t[1]} | Start: {t[2]}:00 | ETA: {t[4]} (+{t[5]} min) | Route: {t[3]}")
    conn.close()

# CLI scheduler
def run_flight_scheduler_cli(user_id):
    airportE = Vertex("E", [])
    airportD = Vertex("D", [airportE])
    airportB = Vertex("B", [airportD, airportE])
    airportC = Vertex("C", [airportB])
    airportA = Vertex("A", [airportC, airportB])
    airport_map = {"A": airportA, "B": airportB, "C": airportC, "D": airportD, "E": airportE}

    flights = [
        Flight('FN-101', airportA, airportB, 6, 2),
        Flight('FN-102', airportA, airportC, 8, 2),
        Flight('FN-103', airportB, airportD, 13, 12),
        Flight('FN-104', airportB, airportE, 17, 11),
        Flight('FN-105', airportC, airportB, 10, 9),
        Flight('FN-106', airportC, airportD, 10, 6),
        Flight('FN-107', airportD, airportE, 14, 13),
    ]
    graph = FlightGraph(list(airport_map.values()))

    print(Fore.CYAN + "\n📍 Available Airports:")
    for code in airport_map:
        print(Fore.YELLOW + f"  {code}", end="  ")
    print("\n")

    source_code = input(Fore.CYAN + "Enter source airport code: ").strip().upper()
    dest_code = input(Fore.CYAN + "Enter destination airport code: ").strip().upper()

    if source_code not in airport_map or dest_code not in airport_map:
        print(Fore.RED + "❌ Invalid airport code.")
        return

    try:
        startT = int(input(Fore.CYAN + "Enter preferred start time (0–23): "))
        if not (0 <= startT <= 23):
            raise ValueError
    except ValueError:
        print(Fore.RED + "❌ Invalid time. Enter an integer between 0 and 23.")
        return

    startVertex, endVertex = airport_map[source_code], airport_map[dest_code]
    arrival_time, path = FlightAgency(flights, graph, startVertex, endVertex, startT)

    if arrival_time != float('inf') and path:
        print(Fore.GREEN + f"\n✅ Itinerary from {startVertex} to {endVertex} starting at {startT}:00\n")
        total_delay = 0
        for flight in path:
            delay = predict_delay(flight)
            total_delay += delay
            print(Fore.MAGENTA + f"{flight} | Predicted Delay: {int(delay)} min")

        print(Fore.YELLOW + f"\n🕓 Total arrival time (without delay): {arrival_time}:00")
        adj_hour = arrival_time + int(total_delay // 60)
        adj_min = int(total_delay % 60)
        print(Fore.RED + f"🕓 Estimated arrival time (with delay): {adj_hour}:{adj_min:02d}")

        # Save itinerary
        save_trip(user_id, source_code, dest_code, startT, path, arrival_time, total_delay)

        # Visuals
        edge_path = [(f.origin.name, f.dest.name) for f in path]
        g = SimpleGraph()
        for f in flights:
            g.add_edge(f.origin.name, f.dest.name, f.arrivalT)
        visualize_graph(g, path_edges=edge_path)
        plot_geo_path(path)
    else:
        print(Fore.RED + "\n❌ No valid flight path found.")

# Visualize graph
def run_visualization():
    g = SimpleGraph()
    g.add_edge("A", "B", 6)
    g.add_edge("A", "C", 8)
    g.add_edge("B", "D", 13)
    g.add_edge("B", "E", 17)
    g.add_edge("C", "B", 10)
    g.add_edge("C", "D", 10)
    g.add_edge("D", "E", 14)
    visualize_graph(g)

# Entry Point
if __name__ == '__main__':
    init_db()  # setup db tables
    print(Fore.BLUE + "🔐 Login or Register:")
    auth_choice = input("1. Login\n2. Register\nChoose 1 or 2: ").strip()

    user_id, username = None, None
    if auth_choice == "1":
        user_id, username = login()
    elif auth_choice == "2":
        register()
        user_id, username = login()

    if not user_id:
        print(Fore.RED + "❌ Authentication failed.")
        exit()

    # After login
    print(Fore.GREEN + f"👋 Welcome, {username}!")
    view = input("🔎 Do you want to view past trips? (y/n): ").strip().lower()
    if view == 'y':
        show_past_trips(user_id)

    print(Fore.BLUE + "\nChoose mode:")
    print(Fore.YELLOW + "1. Flight Scheduler (earliest arrival with delay prediction)")
    print(Fore.YELLOW + "2. Graph Visualization")
    choice = input(Fore.CYAN + "Enter 1 or 2: ")

    if choice == "1":
        run_flight_scheduler_cli(user_id)
    elif choice == "2":
        run_visualization()
    else:
        print(Fore.RED + "Invalid choice.")
