from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import sqlite3
import json
import threading
import time
from datetime import datetime, timedelta
import random
import pickle
import os

app = Flask(__name__)
CORS(app)


class TrafficPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = "models/traffic_model.pkl"
        self.scaler_path = "models/scaler.pkl"
        self.model_info_path = "models/model_info.json"

        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)

        # Try to load existing model
        self.load_model()

    def generate_training_data(self, n_samples=1000):
        """Generate synthetic traffic data for training"""
        data = []
        for _ in range(n_samples):
            hour = random.randint(0, 23)
            day_of_week = random.randint(0, 6)
            weather = random.choice([0, 1, 2])  # 0=sunny, 1=rainy, 2=cloudy

            # Simulate realistic Indian traffic patterns
            base_flow = 80  # Higher base flow for Indian cities
            if 7 <= hour <= 11 or 16 <= hour <= 21:  # Extended rush hours
                base_flow += random.randint(150, 300)  # Much higher congestion
            elif 12 <= hour <= 15:  # Afternoon traffic
                base_flow += random.randint(50, 100)
            elif 22 <= hour or hour <= 5:  # Night time
                base_flow -= random.randint(30, 50)

            if day_of_week >= 5:  # Weekend (still busy in Indian cities)
                base_flow -= random.randint(
                    20, 40
                )  # Less reduction than Western cities

            if weather == 1:  # Monsoon/rainy weather (major impact in India)
                base_flow += random.randint(
                    40, 80
                )  # Higher impact due to poor drainage

            traffic_flow = max(0, base_flow + random.randint(-30, 30))

            data.append(
                {
                    "hour": hour,
                    "day_of_week": day_of_week,
                    "weather": weather,
                    "traffic_flow": traffic_flow,
                }
            )

        return pd.DataFrame(data)

    def save_model(self):
        """Save the trained model and scaler to disk"""
        try:
            # Save the model
            with open(self.model_path, "wb") as f:
                pickle.dump(self.model, f)

            # Save the scaler
            with open(self.scaler_path, "wb") as f:
                pickle.dump(self.scaler, f)

            # Save model information
            model_info = {
                "trained_at": datetime.now().isoformat(),
                "model_type": "RandomForestRegressor",
                "n_estimators": self.model.n_estimators,
                "features": ["hour", "day_of_week", "weather"],
                "is_trained": self.is_trained,
            }

            with open(self.model_info_path, "w") as f:
                json.dump(model_info, f, indent=2)

            print(f"✅ Model saved to {self.model_path}")
            return True

        except Exception as e:
            print(f"❌ Error saving model: {e}")
            return False

    def load_model(self):
        """Load existing model and scaler from disk"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                # Load the model
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)

                # Load the scaler
                with open(self.scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)

                self.is_trained = True

                # Load model info if available
                if os.path.exists(self.model_info_path):
                    with open(self.model_info_path, "r") as f:
                        model_info = json.load(f)
                    print(
                        f"✅ Loaded existing model trained at: {model_info.get('trained_at', 'Unknown')}"
                    )
                else:
                    print("✅ Loaded existing model (no info file)")

                return True
            else:
                print("📝 No existing model found, will train new one")
                return False

        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            print("📝 Will train new model")
            return False

    def train_model(self):
        """Train the ML model with synthetic data"""
        print("🧠 Training ML model...")

        df = self.generate_training_data()

        X = df[["hour", "day_of_week", "weather"]]
        y = df["traffic_flow"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True

        score = self.model.score(X_test_scaled, y_test)
        print(f"Model trained with accuracy: {score:.2f}")

        # Save the trained model
        self.save_model()

        return score

    def predict(self, hour, day_of_week, weather):
        """Predict traffic flow"""
        if not self.is_trained:
            self.train_model()

        features = np.array([[hour, day_of_week, weather]])
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        return max(0, int(prediction))


class IoTSimulator:
    def __init__(self):
        self.sensors = {
            # Delhi NCR - High traffic intersections
            "delhi_cp": {
                "lat": 28.6315,
                "lng": 77.2167,
                "name": "Connaught Place, Delhi",
                "congestion_type": "high",
            },
            "delhi_iffco": {
                "lat": 28.4595,
                "lng": 77.0266,
                "name": "IFFCO Chowk, Gurgaon",
                "congestion_type": "high",
            },
            # Delhi NCR - Medium traffic intersections
            "delhi_lajpat": {
                "lat": 28.5677,
                "lng": 77.2334,
                "name": "Lajpat Nagar, Delhi",
                "congestion_type": "medium",
            },
            "delhi_dwarka": {
                "lat": 28.5921,
                "lng": 77.0460,
                "name": "Dwarka Sector 21, Delhi",
                "congestion_type": "low",
            },
            # Bengaluru - High traffic intersections
            "blr_silk": {
                "lat": 12.9279,
                "lng": 77.6271,
                "name": "Silk Board Junction, Bengaluru",
                "congestion_type": "high",
            },
            "blr_electronic": {
                "lat": 12.8456,
                "lng": 77.6632,
                "name": "Electronic City, Bengaluru",
                "congestion_type": "high",
            },
            # Bengaluru - Medium/Low traffic intersections
            "blr_jayanagar": {
                "lat": 12.9250,
                "lng": 77.5946,
                "name": "Jayanagar 4th Block, Bengaluru",
                "congestion_type": "medium",
            },
            "blr_hebbal": {
                "lat": 13.0358,
                "lng": 77.5970,
                "name": "Hebbal Flyover, Bengaluru",
                "congestion_type": "low",
            },
            # Mumbai - High traffic intersections
            "mumbai_bandra": {
                "lat": 19.0596,
                "lng": 72.8295,
                "name": "Bandra Kurla Complex, Mumbai",
                "congestion_type": "high",
            },
            "mumbai_andheri": {
                "lat": 19.1136,
                "lng": 72.8697,
                "name": "Andheri East, Mumbai",
                "congestion_type": "medium",
            },
            # Chennai - Mixed traffic areas
            "chennai_adyar": {
                "lat": 13.0067,
                "lng": 80.2206,
                "name": "Adyar Signal, Chennai",
                "congestion_type": "medium",
            },
            "chennai_omr": {
                "lat": 12.8406,
                "lng": 80.1534,
                "name": "OMR IT Corridor, Chennai",
                "congestion_type": "low",
            },
        }

    def generate_sensor_data(self):
        """Simulate IoT sensor data"""
        current_time = datetime.now()
        data = []

        for sensor_id, location in self.sensors.items():
            # Simulate realistic Indian traffic patterns with congestion types
            hour = current_time.hour
            congestion_type = location.get("congestion_type", "medium")

            # Base vehicles based on congestion type
            if congestion_type == "high":
                base_vehicles = 60  # High congestion areas
            elif congestion_type == "medium":
                base_vehicles = 35  # Medium congestion areas
            else:  # low congestion
                base_vehicles = 20  # Low congestion areas

            # Indian traffic patterns - longer rush hours, more congestion
            if 7 <= hour <= 11 or 16 <= hour <= 21:  # Extended rush hours
                if congestion_type == "high":
                    base_vehicles += random.randint(100, 180)  # Extreme congestion
                elif congestion_type == "medium":
                    base_vehicles += random.randint(60, 120)  # Moderate congestion
                else:
                    base_vehicles += random.randint(30, 80)  # Light congestion
            elif 12 <= hour <= 15:  # Afternoon traffic
                if congestion_type == "high":
                    base_vehicles += random.randint(40, 80)
                elif congestion_type == "medium":
                    base_vehicles += random.randint(20, 50)
                else:
                    base_vehicles += random.randint(10, 30)
            elif 22 <= hour or hour <= 5:  # Night time
                if congestion_type == "high":
                    base_vehicles = random.randint(15, 35)  # Still busy at night
                elif congestion_type == "medium":
                    base_vehicles = random.randint(8, 20)
                else:
                    base_vehicles = random.randint(3, 12)  # Very light traffic

            # Add city-specific multipliers
            if "mumbai" in sensor_id:  # Mumbai has highest density
                base_vehicles = int(base_vehicles * 1.4)
            elif "delhi" in sensor_id or "blr" in sensor_id:  # Delhi/Bengaluru
                base_vehicles = int(base_vehicles * 1.2)
            elif "chennai" in sensor_id:  # Chennai moderate density
                base_vehicles = int(base_vehicles * 1.1)

            vehicle_count = base_vehicles + random.randint(-15, 15)

            # Speed calculation based on congestion
            if congestion_type == "high":
                avg_speed = max(2, 18 - (vehicle_count * 0.15) + random.randint(-10, 5))
            elif congestion_type == "medium":
                avg_speed = max(5, 28 - (vehicle_count * 0.18) + random.randint(-8, 8))
            else:  # low congestion
                avg_speed = max(8, 40 - (vehicle_count * 0.22) + random.randint(-5, 10))

            data.append(
                {
                    "sensor_id": sensor_id,
                    "timestamp": current_time.isoformat(),
                    "vehicle_count": max(0, vehicle_count),
                    "avg_speed": round(avg_speed, 1),
                    "location": location,
                    "congestion_level": "High"
                    if vehicle_count > 80
                    else "Medium"
                    if vehicle_count > 40
                    else "Low",
                }
            )

        return data


# Initialize components
predictor = TrafficPredictor()
iot_simulator = IoTSimulator()


# Database setup
def init_db():
    conn = sqlite3.connect("traffic_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traffic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT,
            timestamp TEXT,
            vehicle_count INTEGER,
            avg_speed REAL,
            congestion_level TEXT,
            predicted_flow INTEGER
        )
    """)

    conn.commit()
    conn.close()


def store_traffic_data(data):
    """Store traffic data in database"""
    conn = sqlite3.connect("traffic_data.db")
    cursor = conn.cursor()

    for record in data:
        # Get prediction
        current_time = datetime.now()
        predicted_flow = predictor.predict(
            current_time.hour,
            current_time.weekday(),
            random.randint(0, 2),  # Random weather
        )

        cursor.execute(
            """
            INSERT INTO traffic_data 
            (sensor_id, timestamp, vehicle_count, avg_speed, congestion_level, predicted_flow)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                record["sensor_id"],
                record["timestamp"],
                record["vehicle_count"],
                record["avg_speed"],
                record["congestion_level"],
                predicted_flow,
            ),
        )

    conn.commit()
    conn.close()


def data_collection_job():
    """Background job to collect and store data"""
    while True:
        try:
            sensor_data = iot_simulator.generate_sensor_data()
            store_traffic_data(sensor_data)
            print(f"Data collected at {datetime.now()}")
            time.sleep(30)  # Collect data every 30 seconds
        except Exception as e:
            print(f"Error in data collection: {e}")
            time.sleep(30)


# API Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/current-traffic")
def get_current_traffic():
    """Get current traffic data"""
    sensor_data = iot_simulator.generate_sensor_data()

    # Add predictions
    for data in sensor_data:
        current_time = datetime.now()
        predicted_flow = predictor.predict(
            current_time.hour, current_time.weekday(), random.randint(0, 2)
        )
        data["predicted_flow"] = predicted_flow

        # Traffic light recommendation
        if data["congestion_level"] == "High":
            data["light_recommendation"] = "Extend Green"
        elif data["congestion_level"] == "Low":
            data["light_recommendation"] = "Normal Cycle"
        else:
            data["light_recommendation"] = "Optimize Timing"

    return jsonify(sensor_data)


@app.route("/api/predictions")
def get_predictions():
    """Get traffic predictions for next 24 hours"""
    predictions = []
    current_time = datetime.now()

    for i in range(24):
        future_time = current_time + timedelta(hours=i)
        predicted_flow = predictor.predict(
            future_time.hour, future_time.weekday(), random.randint(0, 2)
        )

        predictions.append(
            {
                "hour": future_time.hour,
                "predicted_flow": predicted_flow,
                "timestamp": future_time.isoformat(),
            }
        )

    return jsonify(predictions)


@app.route("/api/historical-data")
def get_historical_data():
    """Get historical traffic data"""
    conn = sqlite3.connect("traffic_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM traffic_data 
        ORDER BY timestamp DESC 
        LIMIT 100
    """)

    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    data = []
    for row in rows:
        data.append(dict(zip(columns, row)))

    conn.close()
    return jsonify(data)


@app.route("/api/analytics")
def get_analytics():
    """Get traffic analytics"""
    conn = sqlite3.connect("traffic_data.db")
    cursor = conn.cursor()

    # Get average traffic by hour
    cursor.execute("""
        SELECT 
            CAST(strftime('%H', timestamp) AS INTEGER) as hour,
            AVG(vehicle_count) as avg_vehicles,
            AVG(avg_speed) as avg_speed
        FROM traffic_data 
        GROUP BY hour
        ORDER BY hour
    """)

    hourly_data = cursor.fetchall()

    # Get congestion distribution
    cursor.execute("""
        SELECT congestion_level, COUNT(*) as count
        FROM traffic_data
        GROUP BY congestion_level
    """)

    congestion_data = cursor.fetchall()

    conn.close()

    return jsonify(
        {
            "hourly_traffic": [
                {"hour": row[0], "avg_vehicles": row[1], "avg_speed": row[2]}
                for row in hourly_data
            ],
            "congestion_distribution": [
                {"level": row[0], "count": row[1]} for row in congestion_data
            ],
        }
    )


if __name__ == "__main__":
    init_db()

    # Start background data collection
    data_thread = threading.Thread(target=data_collection_job, daemon=True)
    data_thread.start()

    # Train the model
    predictor.train_model()

    print("🚦 Smart Traffic Control System Starting...")
    print("📊 Dashboard available at: http://localhost:5000")

    app.run(debug=True, host="0.0.0.0", port=5000)
