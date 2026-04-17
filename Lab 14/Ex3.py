import matplotlib.pyplot as plt
import json

# --- SCATTER PLOT OF FARE VS TRIP MILES ---

try:
    with open("/Users/diuleilomo/Documents/GitHub/ITM-352_S26/Lab 14/Trips from area 8.json") as f:
        trips = json.load(f)
    fares = []
    miles = []
    for trip in trips:
        fare = trip.get("fare")
        trip_miles = trip.get("trip_miles")
        if fare not in [None, "", "NA"] and trip_miles not in [None, "", "NA"]:
            try:
                fares.append(float(fare))
                miles.append(float(trip_miles))
            except (ValueError, TypeError):
                continue

    # Basic scatter plot
    plt.scatter(fares, miles)
    plt.title("Scatter Plot of Fare vs Trip Miles")
    plt.xlabel("Fare")
    plt.ylabel("Trip Miles")
    plt.show()

    # Using plt.plot with linestyle="none" and marker="."
    plt.plot(fares, miles, linestyle="none", marker=".")
    plt.title("Fare vs Trip Miles (plt.plot, marker='.')")
    plt.xlabel("Fare")
    plt.ylabel("Trip Miles")
    plt.show()

    # Fancy plot: cyan, "v" marker, alpha=0.2
    plt.plot(fares, miles, linestyle="none", marker="v", color="cyan", alpha=0.2)
    plt.title("Fare vs Trip Miles (Fancy)")
    plt.xlabel("Fare")
    plt.ylabel("Trip Miles")
    plt.show()

except Exception as e:
    print(f"Could not create scatter plot: {e}")

# Conclusions:
# - If you see an upward trend, longer trips generally cost more.
# - If points are scattered with no pattern, fare and trip miles may not be strongly related.
# - Outliers may indicate unusual trips or data errors.