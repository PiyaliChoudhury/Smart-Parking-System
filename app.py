from flask import Flask, render_template, request, redirect
import joblib
import pandas as pd
import random

app = Flask(__name__)

# Load ML model and scaler
model = joblib.load("parking_model.pkl")
scaler = joblib.load("scaler.pkl")

# SRM Parking Layout
TOTAL_ZONES = 5
PILLARS_PER_ZONE = 50
SLOTS_PER_PILLAR = 10

# Login users
users = {
    "admin": "1234",
    "user": "abcd"
}

# Home page
@app.route("/")
def home():
    return render_template("login.html")


# Login verification
@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username in users and users[username] == password:
        return redirect("/dashboard")

    return "Invalid login"


# Dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", result="")


# Function to check slot availability
def check_slot(zone, pillar, slot, hour, day, vehicle, user):

    data = pd.DataFrame({
        "Zone":[zone],
        "Pillar":[pillar],
        "Slot_Number":[slot],
        "Hour":[hour],
        "Day":[day],
        "Vehicle_Type":[vehicle],
        "User_Type":[user],
        "Rain":[0],
        "Event_Day":[0],
        "Distance_from_gate":[100],
        "Peak_Hour":[1],
        "Weekend":[0],
        "Temperature":[30],
        "Traffic_Level":[5],
        "Exam_Day":[0],
        "Festival_Day":[0],
        "EV_Vehicle":[0],
        "Vehicle_Size":[2],
        "Month":[6],
        "Week_Number":[20],
        "Holiday":[0]
    })

    # Scale features
    data_scaled = scaler.transform(data)

    # Predict
    prediction = model.predict(data_scaled)[0]

    # Add randomness to simulate real parking
    if random.random() < 0.3:
        prediction = 0

    return prediction


# Parking prediction
@app.route("/predict", methods=["POST"])
def predict():

    zone = int(request.form["Zone"])
    pillar = int(request.form["Pillar"])
    slot = int(request.form["Slot_Number"])
    hour = int(request.form["Hour"])
    day = int(request.form["Day"])
    vehicle = int(request.form["Vehicle_Type"])
    user = int(request.form["User_Type"])

    # Check requested slot
    prediction = check_slot(zone, pillar, slot, hour, day, vehicle, user)

    if prediction == 0:

        result = f"Parking Available at Zone {zone}, Pillar {pillar}, Slot {slot}"

        return render_template("dashboard.html", result=result)

    # Search for next available slot (randomized)
    zones = list(range(1, TOTAL_ZONES + 1))
    pillars = list(range(1, PILLARS_PER_ZONE + 1))
    slots = list(range(1, SLOTS_PER_PILLAR + 1))

    random.shuffle(zones)
    random.shuffle(pillars)
    random.shuffle(slots)

    for z in zones:
        for p in pillars:
            for s in slots:

                if check_slot(z, p, s, hour, day, vehicle, user) == 0:

                    result = f"Requested slot occupied. Next available at Zone {z}, Pillar {p}, Slot {s}"

                    return render_template("dashboard.html", result=result)

    # If all slots full
    result = "All parking slots are FULL"

    return render_template("dashboard.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)