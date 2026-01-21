#Ask the User for a number between 1 and 100 square the number and print the number and its square
#Name: Jianbin Xiao
#Date: Jan. 20, 2026

print("Welcome to the Program!")
value_entered = input("Please enter a number between 1 and 100: ")
print("You entered:", value_entered)

value_as_int = int(value_entered)
squared_value = value_as_int ** 2
#print("The square of", value_as_int, "is", squared_value)
print(f"The square of {value_as_int} is {squared_value}")