import pandas as pd

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('/Users/aleksichen/.cache/kagglehub/datasets/atharvasoundankar/chocolate-sales/versions/4/Chocolate Sales.csv')

# Rename columns to match the table schema
df.columns = ['Sales_Person', 'Country', 'Product', 'Date', 'Amount', 'Boxes_Shipped']

# Prepare the data for insertion
data = df.to_dict('records')

# Insert the data into the table
# Note: The actual insert function will be handled by the agent's tools
print("Data prepared for insertion. Ready to insert into Doris.")
data