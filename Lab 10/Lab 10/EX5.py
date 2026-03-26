#Read in a Csv file of homes date and a create a dataframe. 
#Do some filtering and calculations on the data.
import pandas as pd

df_homes = pd.read_csv("/Users/diuleilomo/Documents/GitHub/ITM-352_S26/Lab 10/Lab 10/homes_data.csv")

#print out the shape of the dataframe and the first few rows
shape = df_homes.shape
print(f"The homes data has {shape[0]} rows and {shape[1]} columns.")
print(df_homes.head())

#select only the properties with 500 or more units
df_big_properties = df_homes[df_homes["units"] >= 500]
df_big_properties = df_big_properties.drop(columns=["id",  "easement"])
print(df_big_properties.head(10))