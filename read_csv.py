import pandas as pd

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('/Users/aleksichen/.cache/kagglehub/datasets/atharvasoundankar/chocolate-sales/versions/4/Chocolate Sales.csv')

# Display the first few rows to ensure it's read correctly
print(df.head())