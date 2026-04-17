import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV file
df = pd.read_csv("/Users/diuleilomo/Documents/GitHub/ITM-352_S26/Lab 14/taxi trips Fri 7_7_2017.csv")

# Create a pivot table (matrix) of pickup vs dropoff counts
heatmap_data = pd.pivot_table(
    df,
    index='pickup_community_area',
    columns='dropoff_community_area',
    values='fare',  # or any column, we just want counts
    aggfunc='count',
    fill_value=0
)

plt.figure(figsize=(10, 8))
sns.heatmap(heatmap_data, cmap="YlGnBu")
plt.title("Taxi Trips Heatmap: Pickup vs Dropoff Community Area")
plt.xlabel("Dropoff Community Area")
plt.ylabel("Pickup Community Area")
plt.show()