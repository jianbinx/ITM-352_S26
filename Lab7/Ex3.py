my_tuple = ("hello", 10, "goodbye", 3, "goodnight", 5)
string_count = 0

for element in my_tuple:
    if isinstance(element, str):
        string_count += 1

print(f"There are {string_count} strings in the tuple.")