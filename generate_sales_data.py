import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Generate random sales data
def generate_sales_data(num_rows=200):
    # Define possible products
    products = ["Dark Chocolate", "Milk Chocolate", "White Chocolate", "Caramel Chocolate", "Hazelnut Chocolate"]
    
    # Define possible regions
    regions = ["North", "South", "East", "West"]
    
    # Generate random dates
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    date_range = (end_date - start_date).days
    
    # Generate data
    data = []
    for _ in range(num_rows):
        product = random.choice(products)
        region = random.choice(regions)
        quantity = random.randint(1, 100)
        price = round(random.uniform(1.0, 10.0), 2)
        total_sales = round(quantity * price, 2)
        date = start_date + timedelta(days=random.randint(0, date_range))
        
        data.append({
            "Product": product,
            "Region": region,
            "Quantity": quantity,
            "Price": price,
            "Total_Sales": total_sales,
            "Date": date.strftime("%Y-%m-%d")
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    return df

# Generate and return the DataFrame
sales_data = generate_sales_data()
sales_data