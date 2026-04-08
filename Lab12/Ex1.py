#scrape data from the city of Chicago's data portal
#Print any line that has a <title> tag in it 

import ssl
import  urllib.request
url = "https://data.cityofchicago.org/Historic-Preservation/Landmark-Districts/zidz-sdfj/about_data"
ssl._create_default_https_context = ssl._create_unverified_context

print("Opening URL:" + url)
webpage = urllib.request.urlopen(url)

#iterate through each line in the webpage
for line in webpage:
    #decode the line from bytes to string
    decoded_line = line.decode("utf-8")
    #check if the line contains the <title> tag
    if "<title>" in decoded_line:
        print(line.strip())