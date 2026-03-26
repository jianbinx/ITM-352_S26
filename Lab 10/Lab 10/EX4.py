# Read a json file of taxi trip data and create a dataframe.
# Calculate the median fare
import json
import pandas as pd

taxi_df = pd.read_json("/Users/diuleilomo/Documents/GitHub/ITM-352_S26/Lab 10/Lab 10/Taxi_Trips.json")
print(taxi_df.describe())
print(taxi_df.head())
print("Median Fare:", taxi_df['fare'].median())