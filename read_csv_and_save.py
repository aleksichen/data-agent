import pandas as pd

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('/Users/aleksichen/.cache/kagglehub/datasets/atharvasoundankar/chocolate-sales/versions/4/Chocolate Sales.csv')

# Save the DataFrame to Doris
# Note: The actual save function will be handled by the agent's tools
print(df.head())

# Return the DataFrame for further processing
df