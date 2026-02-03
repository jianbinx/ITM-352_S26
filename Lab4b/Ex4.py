#Parse through the portions of an email address

email = input("Enter your email address: ")

parts = email.split("@")
username = parts[0]
domain = parts[1]

print("Username:", username)
print("Domain:", domain)
