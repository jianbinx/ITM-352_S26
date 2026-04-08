import requests
from bs4 import BeautifulSoup

url = "https://www.hicentral.com/hawaii-mortgage-rates.php"
response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

# Find the rate table (the first table on the page)
table = soup.find("table")

if table:
    rows = table.find_all("tr")
    for row in rows[1:]:  # Skip header row
        cols = [col.get_text(strip=True) for col in row.find_all("td")]
        if cols:
            bank = cols[0]
            rates = cols[1:]
            print(f"Bank: {bank}, Rates: {', '.join(rates)}")
else:
    print("Rate table not found.")