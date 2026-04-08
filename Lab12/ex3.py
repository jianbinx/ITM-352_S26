#parse the ITM Department website to find the people (Faculty, grads, and department staff) and their email addresses. Use the requests library to get the webpage content and BeautifulSoup to parse the HTML and extract the relevant information.
import urllib.request
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
itm_url = "https://shidler.hawaii.edu/itm/people"

itm_html = urllib.request.urlopen(itm_url).read()
html_to_parse = BeautifulSoup(itm_html, "html.parser")

print(html_to_parse.prettify())

#find and print the names of the names of the faculty 
list_of_faculty = html_to_parse.find_all("h2", class_="title")

itm_faculty = []
for person in list_of_faculty:
    name = person.text.strip()
    itm_faculty.append(name)
    print(person.text.strip())