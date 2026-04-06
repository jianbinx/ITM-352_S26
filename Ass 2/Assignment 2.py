import pandas as pd
import numpy as np
import pyarrow
import ssl
import time
import sys

# Allow unverified SSL context for Google Drive
ssl._create_default_https_context = ssl._create_unverified_context

# List of available datasets
datasets = {
    "1": ("Main Sales Data", "https://drive.google.com/uc?id=1Fv_vhoN4sTrUaozFPfzr0NCyHJLIeXEA"),
    "2": ("Alternate Sales Data", "https://drive.google.com/file/d/1Fv_vhoN4sTrUaozFPfzr0NCyHJLIeXEA")
}

def select_dataset():
    print("Select a dataset to load:")
    for key, (name, _) in datasets.items():
        print(f"{key}. {name}")
    choice = input("Enter the number of your choice: ").strip()
    if choice in datasets:
        return datasets[choice][1], datasets[choice][0]
    else:
        print("Invalid choice. Defaulting to Main Sales Data.")
        return datasets["1"][1], datasets["1"][0]

filename, dataset_name = select_dataset()
print(f"Loading {dataset_name}...")

start_time = time.time()
try:
    df = pd.read_csv(filename, engine='pyarrow')
    load_time = time.time() - start_time
    print(f"File loaded successfully in {load_time:.2f} seconds.")
except Exception as e:
    print(f"Error loading file: {e}")
    sys.exit(1)

df = df.fillna(0)

num_rows = df.shape[0]
print(f"Number of rows: {num_rows}")
print(f"Available columns: {list(df.columns)}")

required_fields = {'unit_price', 'region', 'order_type', 'customer_state', 'customer_type', 'order_date', 'quantity', 'product', 'category', 'employee_id'}
missing_fields = required_fields - set(df.columns)

if missing_fields:
    print(f"Warning: Missing fields: {missing_fields}. Some analytics may not work.")
else:
    print("All required fields are present for analytics.")

# --- Dashboard Functions ---

def total_sales_by_region_and_order_type(df):
    if {'unit_price', 'region', 'order_type'} <= set(df.columns):
        pivot = pd.pivot_table(df, values='unit_price', index='region', columns='order_type', aggfunc=np.sum, margins=True)
        return pivot
    else:
        print("Required fields missing.")
        return None

def avg_sales_by_region_state_type(df):
    if {'unit_price', 'region', 'customer_state', 'order_type'} <= set(df.columns):
        pivot = pd.pivot_table(
            df,
            values='unit_price',
            index='region',
            columns=['customer_state', 'order_type'],
            aggfunc=np.mean,
            margins=True
        )
        return pivot
    else:
        print("Required fields missing.")
        return None

def custom_pivot_table(df):
    row_fields = [
        ('employee_name', 'Employee Name'),
        ('region', 'Sales Region'),
        ('product_category', 'Product Category')
    ]
    col_fields = [
        ('order_type', 'Order Type'),
        ('customer_type', 'Customer Type')
    ]
    value_fields = [
        ('quantity', 'Quantity'),
        ('unit_price', 'Unit Price')
    ]
    aggfunc_options = [
        ('sum', np.sum),
        ('mean', np.mean),
        ('count', 'count')
    ]

    def get_selection(options, prompt, allow_empty=False):
        print(prompt)
        for i, (_, label) in enumerate(options, 1):
            print(f"{i}. {label}")
        inp = input("Enter the number(s) of your choice(s), separated by commas" +
                    (" (enter for none): " if allow_empty else ": "))
        if allow_empty and inp.strip() == "":
            return []
        try:
            idxs = [int(x.strip()) - 1 for x in inp.split(",") if x.strip()]
            return [options[i][0] for i in idxs if 0 <= i < len(options)]
        except Exception:
            print("Invalid input.")
            return []

    rows = get_selection(row_fields, "Select rows:")
    if not rows:
        print("You must select at least one row field.")
        return None
    columns = get_selection(col_fields, "Select columns (optional):", allow_empty=True)
    values = get_selection(value_fields, "Select values:")
    if not values:
        print("You must select at least one value field.")
        return None
    aggfuncs = get_selection(aggfunc_options, "Select aggregation function:") #aggfuncs is a list of keys like sum, mean, and count
    if not aggfuncs:
        print("You must select at least one aggregation function.")
        return None

    aggfunc_dict = {val: aggfunc_options[[a[0] for a in aggfunc_options].index(agg)][1]
                    for val in values for agg in aggfuncs}

    try:
        pivot = pd.pivot_table(
            df,
            values=values,
            index=rows,
            columns=columns if columns else None,
            aggfunc=aggfunc_dict if len(aggfuncs) > 1 or len(values) > 1 else aggfunc_options[[a[0] for a in aggfunc_options].index(aggfuncs[0])][1],
            margins=True
        )
        return pivot
    except Exception as e:
        print(f"Error creating custom pivot table: {e}")
        return None

def compare_analytics(df):
    print("\nSelect the first analytic to compare:")
    analytic_functions = [
        ("Total sales by region and order_type", total_sales_by_region_and_order_type),
        ("Average sales by region with average sales by state and sale type", avg_sales_by_region_state_type),
        ("Custom pivot table", custom_pivot_table)
    ]
    for i, (desc, _) in enumerate(analytic_functions, 1):
        print(f"{i}. {desc}")
    try:
        choice1 = int(input("Enter the number of the first analytic: ")) - 1
        choice2 = int(input("Enter the number of the second analytic: ")) - 1
        if 0 <= choice1 < len(analytic_functions) and 0 <= choice2 < len(analytic_functions):
            print("\n--- First Analytic ---")
            result1 = analytic_functions[choice1][1](df)
            print(result1 if result1 is not None else "No result.")
            print("\n--- Second Analytic ---")
            result2 = analytic_functions[choice2][1](df)
            print(result2 if result2 is not None else "No result.")
        else:
            print("Invalid analytic selection.")
    except ValueError:
        print("Invalid input.")

def exit_program():
    print("Exiting dashboard.")
    sys.exit(0)

# --- Menu System ---

def show_first_n_rows():
    print(f"\nThere are {num_rows} rows available.")
    print("Enter rows to display:")
    print(f"- Enter a number 1 to {num_rows}")
    print("- To see all rows, enter 'all'")
    print("- To skip preview, press Enter")
    choice = input("Your choice: ").strip().lower()
    if choice == '':
        print("No preview displayed.")
        return
    if choice == 'all':
        print(df)
        return
    try:
        n = int(choice)
        if 1 <= n <= num_rows:
            print(df.head(n))
        else:
            print(f"Invalid input: Please enter a number between 1 and {num_rows}.")
    except ValueError:
        print("Invalid input: Please enter a valid number, 'all', or press Enter.")

def sales_by_customer_type_and_order_type_by_state(df):
    if {'unit_price', 'customer_type', 'order_type', 'customer_state'} <= set(df.columns):
        pivot = pd.pivot_table(
            df,
            values='unit_price',
            index='customer_state',
            columns=['customer_type', 'order_type'],
            aggfunc=np.sum,
            margins=True
        )
        print("\nSales by customer type and order type by state:")
        print(pivot)
    else:
        print("Required fields missing.")

def total_sales_qty_price_by_region_product(df):
    if {'unit_price', 'quantity', 'sales_region', 'product_category'} <= set(df.columns):
        pivot = pd.pivot_table(
            df,
            values=['unit_price', 'quantity'],
            index='sales_region',
            columns='product_category',
            aggfunc=np.sum,
            margins=True
        )
        print("\nTotal sales quantity and price by region and product:")
        print(pivot)
    else:
        print("Required fields missing.")

def total_sales_qty_price_by_customer_type(df):
    if {'unit_price', 'quantity', 'customer_type', 'order_type'} <= set(df.columns):
        pivot = pd.pivot_table(
            df,
            values=['unit_price', 'quantity'],
            index='customer_type',
            columns='order_type',
            aggfunc=np.sum,
            margins=True
        )
        print("\nTotal sales quantity and price by customer type and order type:")
        print(pivot)
    else:
        print("Required fields missing.")

def max_min_sales_price_by_category(df):
    if {'unit_price', 'product_category'} <= set(df.columns):
        pivot = pd.pivot_table(
            df,
            values='unit_price',
            index='product_category',
            aggfunc=[np.max, np.min],
            margins=True
        )
        print("\nMax and min sales price by product_category:")
        print(pivot)
    else:
        print("Required fields missing.")

def unique_employees_by_region(df):
    if {'employee_id', 'sales_region'} <= set(df.columns):
        pivot = pd.pivot_table(
            df,
            values='employee_id',
            index='sales_region',
            aggfunc=pd.Series.nunique,
            margins=True
        )
        print("\nNumber of unique employees by region:")
        print(pivot)
    else:
        print("Required fields missing.")

# Update your menu_items tuple:
menu_items = (
    ("Show the first n rows of sales data", show_first_n_rows),
    ("Total sales by region and order_type", lambda: print(total_sales_by_region_and_order_type(df))),
    ("Average sales by region with average sales by state and sale type", lambda: print(avg_sales_by_region_state_type(df))),
    ("Sales by customer type and order type by state", lambda: sales_by_customer_type_and_order_type_by_state(df)),
    ("Total sales quantity and price by region and product", lambda: total_sales_qty_price_by_region_product(df)),
    ("Total sales quantity and price customer type", lambda: total_sales_qty_price_by_customer_type(df)),
    ("Max and min sales price of sales by category", lambda: max_min_sales_price_by_category(df)),
    ("Number of unique employees by region", lambda: unique_employees_by_region(df)),
    ("Create a custom pivot table", lambda: print(custom_pivot_table(df))),
    ("Exit", exit_program)
)

def show_menu():
    print("\n--- Sales Data Dashboard ---")
    for i, (item, _) in enumerate(menu_items, 1):
        print(f"{i}. {item}")

while True:
    show_menu()
    try:
        choice = int(input("Select an option: "))
        if 1 <= choice <= len(menu_items):
            menu_items[choice - 1][1]()
        else:
            print("Invalid choice. Please select a valid menu item.")
    except ValueError:
        print("Please enter a number corresponding to a menu item.")