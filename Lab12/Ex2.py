#grab data one month interest rate from the Treasury website  
import ssl
import pandas as pd
import urllib.request
import lxml 

url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202603" 

#Open the url and ise the read_html to reade the data into a dataframe
ssl._create_default_https_context = ssl._create_unverified_context

print("Opening URL:" + url)
webpage = urllib.request.urlopen(url)
data_frames = pd.read_html(webpage)

#print(data_frames[0].info())
#print(data_frames[0]

#print the columns to understand the structure of the dataframe
print("column names in the dataframe:", data_frames[0].columns)

#extract the date and the 1 month interest rate from the dataframe
one_month_rate = data_frames[0].iloc[0, "1 Mo"]

print("One month interest rate:", one_month_rate)