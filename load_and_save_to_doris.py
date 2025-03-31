import pandas as pd

# Load the temporary CSV file into a DataFrame
temp_file = "temp_chocolate_sales.csv"
data = pd.read_csv(temp_file)

# Save the DataFrame to Doris using the 'save_to_file_and_run' function
# Replace 'chocolate_sales' with the actual table name if different
# Also, ensure the necessary credentials and connection details are configured in the environment
save_to_file_and_run(
    file_name="save_to_doris.py",
    code=f"""
import pandas as pd

data = pd.read_csv('{temp_file}')

save(
    table='chocolate_sales',
    df=data,
    if_exists='replace',
    table_description='Chocolate sales dataset downloaded from Kaggle',
    column_descriptions={{
        'column1': 'Description for column1',
        'column2': 'Description for column2'
        # Add descriptions for all columns as needed
    }}
)

print("Data successfully saved to Doris.")
""",
    variable_to_return=None,
    overwrite=True
)

print("Data successfully saved to Doris.")