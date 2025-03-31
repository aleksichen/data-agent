import pandas as pd

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('/Users/aleksichen/.cache/kagglehub/datasets/atharvasoundankar/chocolate-sales/versions/4/Chocolate Sales.csv')

# Save the DataFrame to a Doris table
# The actual save function will be handled by the system
print("DataFrame ready to be saved to Doris.")
print(df.head())