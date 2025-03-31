import pandas as pd

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('/Users/aleksichen/.cache/kagglehub/datasets/atharvasoundankar/chocolate-sales/versions/4/Chocolate Sales.csv')

# Save the DataFrame to a file for later use
df.to_pickle('chocolate_sales_dataframe.pkl')
print("DataFrame saved to 'chocolate_sales_dataframe.pkl'.")