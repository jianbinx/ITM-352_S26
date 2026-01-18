#!/usr/bin/env python3
# Simple Calculator Program

print("=== Simple Calculator ===")

while True:
    try:
        # Get two numbers from user
        num1 = float(input("\nEnter first number: "))
        num2 = float(input("Enter second number: "))
        
        # Display operation choices
        print("\nChoose an operation:")
        print("1. Add (+)")
        print("2. Subtract (-)")
        print("3. Multiply (*)")
        print("4. Divide (/)")
        
        # Get operation choice
        operation = input("\nEnter operation (1/2/3/4) or symbol (+/-/*//): ")
        
        # Perform calculation
        if operation == '1' or operation == '+':
            result = num1 + num2
            print(f"\n{num1} + {num2} = {result}")
        
        elif operation == '2' or operation == '-':
            result = num1 - num2
            print(f"\n{num1} - {num2} = {result}")
        
        elif operation == '3' or operation == '*':
            result = num1 * num2
            print(f"\n{num1} * {num2} = {result}")
        
        elif operation == '4' or operation == '/':
            if num2 == 0:
                print("\nError: Cannot divide by zero!")
            else:
                result = num1 / num2
                print(f"\n{num1} / {num2} = {result}")
        
        else:
            print("\nError: Invalid operation selected!")
        
        # Ask if user wants to continue
        again = input("\nDo another calculation? (yes/no): ").lower()
        if again != 'yes' and again != 'y':
            print("Thank you for using the calculator!")
            break
    
    except ValueError:
        print("Error: Please enter valid numbers!")
