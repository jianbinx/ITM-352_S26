import pandas as pd
import numpy as np

filename = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K"

pd.set_option('display.max_columns', None)  # Show all columns

try:
    # Read CSV with pyarrow backend, skip bad lines
    df = pd.read_csv(
        filename,
        dtype_backend="pyarrow",
        on_bad_lines='skip'  # skip lines with errors
    )
    print("File loaded successfully.")
except Exception as e:
    print(f"Error loading file: {e}")
    df = None

if df is not None:
    # Convert order_date to datetime
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    print(df.head())
    print(df.dtypes)
else:
    print("No data to display.")

'''
**Explanation:**
- **Exception handling** ensures your program doesn't crash if the file can't be loaded or there are read errors; it lets you handle problems gracefully.
- **pyarrow backend** allows for more efficient memory usage and better support for large datasets and missing values.
- **skip bad lines** prevents the read from failing due to corrupted or malformed rows, so you can still work with the rest of the data.
- **Converting data types while reading** is more efficient and avoids extra passes over the data, reducing memory and processing time.
- **Converting order_date to datetime** ensures consistent date formatting, enables date-based filtering, and avoids errors in date calculations.
- **Warnings** (such as about bad lines or conversion issues) can be addressed by using `on_bad_lines='skip'` and `errors='coerce'` for date conversion, which will set problematic dates to NaT (Not a Time) instead of raising errors.
'''