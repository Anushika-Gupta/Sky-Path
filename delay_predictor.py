import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

# ✅ Sample dataset
data = {
    'origin': ['A', 'A', 'B', 'C', 'B', 'C', 'D'],
    'dest':   ['B', 'C', 'D', 'B', 'E', 'D', 'E'],
    'departT': [2, 2, 12, 9, 11, 6, 13],
    'day': ['Mon', 'Tue', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    'weather': ['Clear', 'Clear', 'Rain', 'Clear', 'Storm', 'Clear', 'Fog'],
    'delay_min': [5, 3, 12, 7, 25, 10, 15]
}

df = pd.DataFrame(data)

# Encode categorical features
le_origin = LabelEncoder()
le_dest = LabelEncoder()
le_day = LabelEncoder()
le_weather = LabelEncoder()

df['origin'] = le_origin.fit_transform(df['origin'])
df['dest'] = le_dest.fit_transform(df['dest'])
df['day'] = le_day.fit_transform(df['day'])
df['weather'] = le_weather.fit_transform(df['weather'])

# Features and target
X = df[['origin', 'dest', 'departT', 'day', 'weather']]
y = df['delay_min']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Save model and encoders
joblib.dump(model, 'delay_model.pkl')
joblib.dump((le_origin, le_dest, le_day, le_weather), 'label_encoders.pkl')

print("✅ Model and encoders saved successfully.")
