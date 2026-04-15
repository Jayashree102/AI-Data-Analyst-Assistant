import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Generate basic data
dates = pd.date_range(start='2023-01-01', periods=150, freq='D')
categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']

data = {
    'Transaction_ID': range(1001, 1151),
    'Date': dates,
    'Category': np.random.choice(categories, 150),
    'Quantity': np.random.randint(1, 20, 150),
    'Unit_Price': np.random.uniform(10.0, 300.0, 150).round(2),
    'Discount_Pct': np.random.choice([0, 5, 10, 15, 20], 150)
}

df = pd.DataFrame(data)

# Calculate Revenue
df['Revenue'] = (df['Quantity'] * df['Unit_Price']) * (1 - df['Discount_Pct']/100)
df['Revenue'] = df['Revenue'].round(2)

# Inject intentional data quality issues for the assistant to clean:
# 1. Add some missing values
df.loc[12:18, 'Category'] = np.nan
df.loc[45:50, 'Unit_Price'] = np.nan
df.loc[100:105, 'Discount_Pct'] = np.nan

# 2. Add some duplicate rows
duplicates = df.iloc[30:35].copy()
df = pd.concat([df, duplicates], ignore_index=True)

# 3. Add an outlier
df.loc[75, 'Quantity'] = 1500  # Massive outlier

# Save to CSV
df.to_csv('sample_sales_data.csv', index=False)
print("sample_sales_data.csv successfully generated!")
