import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi

# Initialize Kaggle API
api = KaggleApi()
api.authenticate()

# Download the dataset
api.dataset_download_files('atharvasoundankar/chocolate-sales', path='.', unzip=True)

# Read the downloaded data (assuming the file is named 'chocolate_sales.csv')
data = pd.read_csv('chocolate_sales.csv')

# Return the data for further processing
data