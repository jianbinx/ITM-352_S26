with open("names.txt", "r") as file_object:
    contents = file_object.read()
    names_list = [name for name in contents.split("\n") if name.strip()]
    print(f"Number of names: {len(names_list)}")