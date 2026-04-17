import matplotlib.pyplot as plt
import importlib.util
import json

# ...existing code...

# --- SCATTER PLOT OF FARES AND TIPS ---

try:
    with open("/Users/diuleilomo/Documents/GitHub/ITM-352_S26/Lab 14/Trips_Fri07072017T4 trip_miles gt1.json") as f:
        trips = json.load(f)
    fares = []
    tips = []
    for trip in trips:
        fare = trip.get("fare")
        tip = trip.get("tips")
        if fare not in [None, "", "NA"] and tip not in [None, "", "NA"]:
            try:
                fares.append(float(fare))
                tips.append(float(tip))
            except (ValueError, TypeError):
                continue

    plt.scatter(fares, tips, color='purple', alpha=0.6)
    plt.title("Scatter Plot of Fares vs Tips")
    plt.xlabel("Fare")
    plt.ylabel("Tips")
    plt.show()
except Exception as e:
    print(f"Could not create scatter plot: {e}")

# Conclusions:
# - If the scatter plot shows an upward trend, higher fares tend to have higher tips.
# - If points are scattered with no pattern, there may be little or no relationship between fare and tip.
# - Outliers (very high fares or tips) may indicate unusual trips or errors in the data.