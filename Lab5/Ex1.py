country_capitals = {
    "France": "Paris",
    "Germany": "Berlin",
    "Italy": "Rome"}

print(country_capitals)

print(country_capitals["France"])
print(country_capitals["Germany"])

country_capitals["Spain"] = "Madrid"
print(country_capitals)

country_capitals["Italy"] = "Milan"
print(country_capitals)

print("Germany" in country_capitals)
print("Portugal" not in country_capitals)
print("Korea" in country_capitals)