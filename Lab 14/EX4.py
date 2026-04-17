import matplotlib.pyplot as plt
import json

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
                fare_val = float(fare)
                miles_val = float(trip_miles)
                # Filter out trips of 0 miles and less than 2 miles
                if miles_val >= 2:
                    fares.append(fare_val)
                    miles.append(miles_val)
            except (ValueError, TypeError):
                continue

    plt.scatter(fares, miles, color="blue", alpha=0.6)
    plt.title("Fare vs Trip Miles (Trips >= 2 miles)")
    plt.xlabel("Fare")
    plt.ylabel("Trip Miles")
    plt.savefig("FaresXmiles.png")
    plt.show()

except Exception as e:
    print(f"Could not create scatter plot: {e}")

# Anomalies you might notice:
# - Some trips may have high fares for relatively short distances (possible outliers or data entry errors).
# - Some points may cluster at certain fare or mile values, indicating common trip types or flat rates.
# - If there are any points with extremely high or low fares for the given miles, these could be anomalies.