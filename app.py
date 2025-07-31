import streamlit as st
import pandas as pd
from flight import Flight, Vertex, Graph as FlightGraph, FlightAgency
from graph import Graph as SimpleGraph
from geo_visualize import plot_geo_path
from database import get_db_path, init_db
import sqlite3
import joblib
import os

# --------------- Initialization -----------------
init_db()
st.set_page_config(page_title="SkyPath ✈️", layout="centered")

# --------------- Banner Image -----------------
st.image("code/banner.png", use_container_width=True)

# --------------- Load ML Model & Encoders -----------------
model = joblib.load("delay_model.pkl")
le_origin, le_dest, le_day, le_weather = joblib.load("label_encoders.pkl")

# --------------- Load Dataset -----------------
csv_path = "C:/Users/anush/Desktop/airport-route-planner/flight-agenda-dijkstra-1/data/indian_routes/Indian-Airlines-Dataset.csv"
df = pd.read_csv(csv_path).dropna()

# Build Graph from Data
airports = sorted(set(df['source']).union(set(df['dest'])))
airport_vertices = {code: Vertex(code, []) for code in airports}

for _, row in df.iterrows():
    src = airport_vertices[row['source']]
    dest = airport_vertices[row['dest']]
    if dest not in src.adjacentVertices:
        src.adjacentVertices.append(dest)

flights = []
for _, row in df.iterrows():
    dep = 2
    arr = dep + 1
    flights.append(Flight(row['fltno'], airport_vertices[row['source']], airport_vertices[row['dest']], arr, dep))

graph = FlightGraph(list(airport_vertices.values()))

# ----------------- Auth Helpers ------------------
def authenticate_user(username, password):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    result = cur.fetchone()
    conn.close()
    return result

def register_user(username, password):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def show_user_trips(user_id):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute("SELECT start, end, start_time, itinerary, arrival_time, delay_minutes FROM trips WHERE user_id = ?", (user_id,))
    trips = cur.fetchall()
    conn.close()
    return trips

def predict_delay(flight):
    try:
        features = pd.DataFrame([{
            'origin': le_origin.transform([flight.origin.name])[0],
            'dest': le_dest.transform([flight.dest.name])[0],
            'departT': flight.departT,
            'day': 2,
            'weather': 0
        }])
        return model.predict(features)[0]
    except:
        return 0

# ---------------- Login Page ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to SkyPath")

    login_tab, register_tab = st.tabs(["🔑 Login", "📝 Register"])

    with login_tab:
        uname = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(uname, pwd)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = uname
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with register_tab:
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")
        if st.button("Register"):
            register_user(new_user, new_pass)
            st.success("✅ Registration successful! Please login.")
    st.stop()

# ---------------- Main App ------------------
st.sidebar.success(f"👋 Welcome, {st.session_state.username}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("✈️ SkyPath – Smart Flight Route Scheduler")

col1, col2 = st.columns(2)
with col1:
    source = st.selectbox("From (Source Airport):", airports)
with col2:
    destination = st.selectbox("To (Destination Airport):", airports)

start_time = st.slider("🕒 Choose Start Time (0–23):", 0, 23, 2)

if st.button("🔍 Find Best Route"):
    if source == destination:
        st.error("⚠️ Source and destination can't be the same.")
    else:
        start_v = airport_vertices[source]
        dest_v = airport_vertices[destination]
        arrival_time, path = FlightAgency(flights, graph, start_v, dest_v, start_time)

        if path:
            st.success(f"📍 Route found from **{source}** to **{destination}**")

            total_delay = 0
            st.subheader("🧾 Itinerary")
            for flight in path:
                delay = predict_delay(flight)
                total_delay += delay
                emoji = "⚠️" if delay > 10 else "✅"
                st.markdown(f"{emoji} **{flight}** | Delay: `{int(delay)} min`")

            # Show summary
            st.subheader("🕓 Timing Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Arrival (No Delay)", f"{arrival_time}:00")
            with col2:
                adj_hour = arrival_time + int(total_delay // 60)
                adj_min = int(total_delay % 60)
                st.metric("With Delay", f"{adj_hour}:{adj_min:02d}")

            # Save trip
            try:
                conn = sqlite3.connect(get_db_path())
                cursor = conn.cursor()
                itinerary_str = " → ".join([f.origin.name for f in path] + [path[-1].dest.name])
                cursor.execute("""INSERT INTO trips (user_id, start, end, start_time, itinerary, arrival_time, delay_minutes)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)""",
                               (st.session_state.user_id, source, destination, start_time, itinerary_str, f"{arrival_time}:00", int(total_delay)))
                conn.commit()
                conn.close()
            except Exception as e:
                st.error(f"❌ Failed to save trip: {e}")

            # Plot map
            plot_geo_path(path)
            st.markdown("🗺️ **Route Map:**")
            with open("flight_path_map.html", "r", encoding="utf-8") as f:
                map_html = f.read()
            st.components.v1.html(map_html, height=500)
        else:
            st.error("❌ No valid path found.")

# ---------------- Show Past Trips ------------------
with st.expander("📒 View Your Saved Trips"):
    trips = show_user_trips(st.session_state.user_id)
    if trips:
        st.markdown("### 🧳 Past Itineraries")
        for t in trips:
            st.markdown(f"🔸 **{t[0]} → {t[1]}** | Start: {t[2]}:00 | ETA: {t[4]} (+{t[5]} min) | Route: `{t[3]}`")
    else:
        st.info("No saved trips found.")

# ---------------- Footer ------------------
st.markdown("---")
st.markdown("✅ *Project: SkyPath – Smart Flight Route Scheduler*")
st.markdown("👩‍💻 *By Anushika Gupta*")
