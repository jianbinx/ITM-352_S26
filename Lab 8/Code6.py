# Write code that will iterate through numbers from 1 to 10 and print 
# the number if it is not equal to 5 (using continue) and stop the 
# loop entirely and print a message when it reaches 8 (using break).

   
for number in range(1, 11):
    
    if number == 5:
        continue   # Skip printing 5
    
    if number == 8:
        print("Break!")
        break      # Stop the loop completely
    
    print(number)