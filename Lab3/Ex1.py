#This program demonstrates variable scope in Python.
#Name: Jianbin Xiao
#Date: Jan. 27, 2026

def calculate_discounted_price(price):
    final_price *= price - discount
    print(f"inside function, discounted_price: (price.2f)")
    return price

discount = 0.6
price=100
print(f"original price before function call, price: {price:.2f}")
discounted_price = calculate_discounted_price(price, discount)

print(f"original price after function call, price: {price:.2f}")
print("Discount=", discount)

