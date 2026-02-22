prices = (2.99, 5.49, 1.99, 3.50)

total = 0

for price in prices:
    discounted_price = price * 0.9 
    total += price

round_total = round(total, 2)
print(f"The total price of the items is: ${round_total:.2f}")