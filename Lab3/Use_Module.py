from Handy_math import max, min, midpoint, exponent, sqrt

number1 = float(input("Enter the first number: "))
number2 = float(input("Enter the second number: "))

mid = midpoint(number1, number2)
print(f"The midpoint between {number1} and {number2} is {mid}.")

exp = exponent(number1, number2, 3)
print(f"{number1} raised to the power of {number2} is approximately {exp}.")

max_value = max(number1, number2)
print(max_value.__module__)
print(f"The maximum of {number1} and {number2} is {max_value}.")

min_value = min(number1, number2)
print(f"The minimum of {number1} and {number2} is {min_value}.")

sqrt1 = sqrt(number1)
print(f"The square root of {number1} is {sqrt1}.")