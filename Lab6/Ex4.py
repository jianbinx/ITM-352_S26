def isLeapYear(year):
    """
    Determine if a year is a leap year using if-statements.
    Returns "Leap year" or "Not a leap year".
    """
    if year % 4 != 0:
        return "Not a leap year"
    elif year % 100 != 0:
        return "Leap year"
    elif year % 400 == 0:
        return "Leap year"
    else:
        return "Not a leap year"

# Test cases
def test_isLeapYear():
    test_cases = [
        (1996, "Leap year"),
        (2000, "Leap year"),
        (1900, "Not a leap year"),
        (2001, "Not a leap year"),
        (2024, "Leap year"),
        (2100, "Not a leap year"),
    ]
    for year, expected in test_cases:
        result = isLeapYear(year)
        print(f"Year {year}: {result} ({'PASS' if result == expected else 'FAIL'})")

if __name__ == "__main__":
    test_isLeapYear()