import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json

try:
    with open("/Users/diuleilomo/Documents/GitHub/ITM-352_S26/Lab 14/Trips from area 8.json") as f:
        trips = json.load(f)
    fares = []
    miles = []
    dropoff_areas = []
    for trip in trips:
        fare = trip.get("fare")
        trip_miles = trip.get("trip_miles")
        dropoff_area = trip.get("dropoff_community_area")
        if (fare not in [None, "", "NA"] and
            trip_miles not in [None, "", "NA"] and
            dropoff_area not in [None, "", "NA"]):
            try:
                fares.append(float(fare))
                miles.append(float(trip_miles))
                dropoff_areas.append(float(dropoff_area))
            except (ValueError, TypeError):
                continue

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(fares, miles, dropoff_areas, c='green', marker='o', alpha=0.5)
    ax.set_title("3D Plot: Fare, Trip Miles, Dropoff Area")
    ax.set_xlabel("Fare")
    ax.set_ylabel("Trip Miles")
    ax.set_zlabel("Dropoff Area")
    plt.show()

except Exception as e:
    print(f"Could not create 3D plot: {e}")