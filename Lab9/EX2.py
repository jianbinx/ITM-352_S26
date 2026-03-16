import csv

salaries = []

# Open the CSV file
with open("Employee_Data.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        salaries.append(float(row["Annual_Salary"]))

# Calculate statistics
average_salary = sum(salaries) / len(salaries)
max_salary = max(salaries)
min_salary = min(salaries)

# Display results
print("Average Salary:", average_salary)
print("Maximum Salary:", max_salary)
print("Minimum Salary:", min_salary)