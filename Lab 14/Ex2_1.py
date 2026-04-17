import matplotlib.pyplot as plt
import importlib.util
import json

# Checks if SciPy, statsmodels, and matplotlib are installed
packages = ['scipy', 'statsmodels', 'matplotlib']
for pkg in packages:
    if importlib.util.find_spec(pkg) is not None:
        print(f"{pkg} is installed.")
    else:
        print(f"{pkg} is NOT installed.")

# Define first set of values
x1 = [1, 2, 3, 4, 5]
y1 = [2, 4, 6, 8, 10]

# Define second set of values
x2 = [1, 2, 3, 4, 5]
y2 = [1, 3, 5, 7, 9]

# Plot first set as a line graph
plt.plot(x1, y1, label='Line 1', marker='o')

# Plot first set as a scatter plot
plt.scatter(x1, y1, color='blue', label='Scatter 1')

# Plot second set as a line graph
plt.plot(x2, y2, label='Line 2', linestyle='--', color='red', marker='s')

# Add title and axis labels
plt.title("Line and Scatter Plot Example")
plt.xlabel("X values")
plt.ylabel("Y values")
plt.legend()
plt.show()

# --- HISTOGRAM FROM TRIP MILES DATA ---

try:
    with open("/Users/diuleilomo/Documents/GitHub/ITM-352_S26/Lab 14/Trips from area 8.json") as f:
        trips = json.load(f)
    # Assume each trip is a dict with a "trip_miles" field
    trip_miles = [float(trip["trip_miles"]) for trip in trips if "trip_miles" in trip]
    
    plt.hist(trip_miles, bins=20, color='green', edgecolor='black')
    plt.title("Histogram of Trip Miles")
    plt.xlabel("Trip Miles")
    plt.ylabel("Frequency")
    plt.show()
except Exception as e:
    print(f"Could not create histogram: {e}")

# --- SECOND HISTOGRAM: PAYMENT METHOD vs SUM OF TIPS ---

try:
    # Drop rows with NA values for 'payment_type' or 'tips'
    filtered_trips = [
        trip for trip in trips
        if trip.get("payment_type") not in [None, "", "NA"] and trip.get("tips") not in [None, "", "NA"]
    ]
    # Aggregate sum of tips by payment method
    tip_sums = {}
    for trip in filtered_trips:
        payment = str(trip["payment_type"])
        try:
            tip = float(trip["tips"])
        except (ValueError, TypeError):
            continue
        tip_sums[payment] = tip_sums.get(payment, 0) + tip

    # Prepare data for bar plot
    payment_methods = list(tip_sums.keys())
    total_tips = [tip_sums[pm] for pm in payment_methods]

    plt.bar(payment_methods, total_tips, color='orange', edgecolor='black')
    plt.title("Total Tips by Payment Method")
    plt.xlabel("Payment Method")
    plt.ylabel("Total Tips")
    plt.show()
except Exception as e:
    print(f"Could not create payment method histogram: {e}")