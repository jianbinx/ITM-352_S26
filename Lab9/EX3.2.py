import csv

filename = "taxi_1000.csv"
fares = []
trip_miles = []

with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)
    fare_index = headers.index("Fare")
    miles_index = headers.index("Trip Miles")

    for row in reader:
        try:
            fare = float(row[fare_index])
            miles = float(row[miles_index])
            if fare > 10:
                fares.append(fare)
                trip_miles.append(miles)
        except (ValueError, IndexError):
            continue  # Skip rows with invalid data

if fares:
    total_fares = sum(fares)
    average_fare = total_fares / len(fares)
    max_trip_miles = max(trip_miles)
    print(f"Total fares over $10: ${total_fares:.2f}")
    print(f"Average fare over $10: ${average_fare:.2f}")
    print(f"Maximum trip miles for fares over $10: {max_trip_miles:.2f}")
else:
    print("No fares over $10 found.")