# a. Open the file and display the data type returned from open()
file_object = open("names.txt", "r")
print(f"Type returned from open(): {type(file_object)}")

# This is more useful than immediately reading/writing because the file object
# allows you to read, write, iterate, or process the file in various ways as needed.

# b. Read the contents and print the number of names
contents = file_object.read()
names_list = [name for name in contents.split("\n") if name.strip()]
print(f"Number of names: {len(names_list)}")
file_object.close()