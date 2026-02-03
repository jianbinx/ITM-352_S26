#An example of creating and user own function.
#Name: Jianbin Xiao
#Date: Jan. 22, 2026
import datetime


def greet_user(name):
    """This function greets the user by their name."""
    print(f"Hello, {name}! Welcome to the program.")
    message = f"It's great to have you here, {name}."
    return message  

user_name = input("Please enter your name: ")
greeting_message = greet_user(user_name)
print(greeting_message)
