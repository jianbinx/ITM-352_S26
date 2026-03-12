# Program to remove any scores from a list that are below 50.
 
scores = [60, 45, 30, 85, 10, 90]

# Use list comprehension to filter scores
scores = [score for score in scores if score >= 50]
print(scores)
