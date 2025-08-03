✈️ SkyPath – Smart Flight Route Scheduler
SkyPath is an intelligent flight route planning app built with Streamlit. It helps users find the shortest flight paths between airports, predict delays using machine learning, and manage trip data, all in a sleek and user-friendly interface.

Features
- Route Planner: Visualize the shortest route between airports using Dijkstra’s algorithm.
- Interactive Maps: Real-world map view powered by Pydeck for intuitive path visualization.
- Flight Delay Prediction: ML-based delay prediction using synthetic datasets and linear regression.
- Trip Management: User login/registration with saved trip history using SQLite.
- Graph View: NetworkX-based route graphs with airport connectivity visualization.
- Summary Dashboard: Quick stats on saved trips, delay predictions, and airport connectivity.

Technologies Used
- Python, Streamlit
- NetworkX, Pydeck, GeoMap
- SQLite, Pandas, Scikit-learn
- Matplotlib, Folium 

ML Model
The delay predictor is trained on synthetic flight data using linear regression and label encoding. It's designed to simulate real-world flight delays for demo purposes.

License
This project is licensed under the MIT License — feel free to use, modify, and share it.

