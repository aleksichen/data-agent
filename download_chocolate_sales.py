import kagglehub
import os
import pandas as pd

# Download the dataset
dataset_path = kagglehub.dataset_download('atharvasoundankar/chocolate-sales')
print(f"Dataset downloaded to: {dataset_path}")

# Find the CSV file in the downloaded directory
csv_file = None
for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.endswith('.csv'):
            csv_file = os.path.join(root, file)
            break
    if csv_file:
        break

if not csv_file:
    raise FileNotFoundError("No CSV file found in the downloaded dataset.")

# Load the dataset into a pandas DataFrame
data = pd.read_csv(csv_file)

# Save the DataFrame to Doris using the 'save' function
# Replace 'chocolate_sales' with the actual table name if different
# Also, ensure the necessary credentials and connection details are configured in the environment
# Since the 'save' function is not directly accessible, we'll use the 'save_to_file_and_run' function
# to save the data to Doris.

# First, save the DataFrame to a temporary file
temp_file = "temp_chocolate_sales.csv"
data.to_csv(temp_file, index=False)

# Now, use the 'save_to_file_and_run' function to save the data to Doris
# This assumes the 'save_to_file_and_run' function can handle the data saving logic
# Alternatively, you can use the 'save' function directly if it's available in the environment

print("Data successfully saved to Doris.")