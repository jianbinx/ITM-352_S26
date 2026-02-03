def sqrt(number):
    if number < 0:
        return None
    return number ** 0.5

number_input = float(input("Enter a number to find its square root: "))

result = sqrt(number_input)
if result is None:
    print("Cannot compute the square root of a negative number.")
else:
    print(f"The square root of {number_input} is {result}.")