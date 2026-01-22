#Ask the user to enter a temperature in farenheit.
#Convert the temperature to celsius using the formula:C = (F - 32) * 5/9
#Name: Jianbin Xiao
#Date: Jan. 22, 2026

farenheit_input = input("Please enter a temperature in farenheit: ")
farenheit_float = float(farenheit_input)
celsius_value = (farenheit_input - 32) * 5 / 9
celsius_value_rounded = round(celsius_value, 1)

print("You entered:", farenheit_input)
print(f"The temperature in celsius is {celsius_value_rounded}")
