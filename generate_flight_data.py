import pandas as pd
import random

origins = ['A', 'B', 'C', 'D']
destinations = ['B', 'C', 'D', 'E']
weather_conditions = ['Clear', 'Rainy', 'Stormy', 'Foggy']
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

data = []

for i in range(200):
    origin = random.choice(origins)
    dest = random.choice([d for d in destinations if d != origin])
    flight_id = f"FN-{100 + i}"
    departure_hour = random.randint(0, 23)
    day = random.choice(days)
    weather = random.choice(weather_conditions)

    # Simulate delay
    base_delay = 5
    delay = base_delay
    if weather == 'Rainy': delay += 10
    if weather == 'Stormy': delay += 20
    if weather == 'Foggy': delay += 15
    if 17 <= departure_hour <= 20: delay += 5  # Rush hour
    delay += random.randint(0, 10)  # noise

    data.append([flight_id, origin, dest, departure_hour, day, weather, delay])

df = pd.DataFrame(data, columns=[
    'FlightID', 'Origin', 'Destination', 'DepartureHour', 'Day', 'Weather', 'Delay'
])
df.to_csv('flight_delay_data.csv', index=False)
print("✅ Synthetic data generated as 'flight_delay_data.csv'")
