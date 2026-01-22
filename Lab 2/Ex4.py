#Ask the user to enter a floating point number. Square the number.
#Print out the original number and its squared result.
#Name: Jianbin Xiao
#Date: Jan. 22, 2026

input_value = input("Please enter a floating point number: ")
print("You entered:", input_value)
squared_value = float(input_value) ** 2

#round the number to 2 decimal places
squared_value = round(squared_value, 2)

print("You entered:", input_value)
print(f"The square of {input_value} is {squared_value}")