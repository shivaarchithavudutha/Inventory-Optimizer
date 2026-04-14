import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. Setup Parameters
np.random.seed(42)
num_days = 365
# Generic products
products = {
    'Premium Detergent': {'cost': 15, 'holding_cost': 1.5, 'lead_time': 5},
    'Personal Grooming Kit': {'cost': 25, 'holding_cost': 2.5, 'lead_time': 7},
    'Bulk Shampoo': {'cost': 8, 'holding_cost': 0.8, 'lead_time': 4},
    'Daily Deodorant': {'cost': 5, 'holding_cost': 0.5, 'lead_time': 3},
    'Skin Care Cream': {'cost': 30, 'holding_cost': 4.0, 'lead_time': 10}
}

data = []
start_date = datetime(2025, 1, 1)

for product, specs in products.items():
    for day in range(num_days):
        date = start_date + timedelta(days=day)
        # Base demand + randomness + weekend surge
        base_demand = np.random.randint(15, 45)
        weekday_effect = 1.3 if date.weekday() >= 5 else 1.0 
        sales = int(base_demand * weekday_effect)
        
        data.append({
            'Date': date,
            'Product': product,
            'Units_Sold': sales,
            'Unit_Cost': specs['cost'],
            'Holding_Cost_Per_Unit': specs['holding_cost'],
            'Lead_Time_Days': specs['lead_time'],
            'Ordering_Cost': 100 # Fixed cost to place one order
        })

df = pd.DataFrame(data)
df.to_csv('supply_chain_data.csv', index=False)
print("Step 1 Complete: Dataset 'supply_chain_data.csv' created.")

import math

# 1. Aggregate data per product to find Annual Demand and Standard Deviation
stats = df.groupby('Product').agg(
    Annual_Demand=('Units_Sold', 'sum'),
    Daily_Demand_Std=('Units_Sold', 'std'),
    Avg_Daily_Demand=('Units_Sold', 'mean'),
    Unit_Cost=('Unit_Cost', 'first'),
    Holding_Cost=('Holding_Cost_Per_Unit', 'first'),
    Lead_Time=('Lead_Time_Days', 'first'),
    Order_Cost=('Ordering_Cost', 'first')
).reset_index()

# 2. EOQ Formula: sqrt((2 * Demand * Order_Cost) / Holding_Cost)
def calculate_eoq(row):
    eoq = math.sqrt((2 * row['Annual_Demand'] * row['Order_Cost']) / row['Holding_Cost'])
    return round(eoq)

# 3. Safety Stock Formula: Service_Level_Factor (1.65 for 95%) * StdDev * sqrt(Lead_Time)
def calculate_safety_stock(row):
    service_factor = 1.65 # Covers 95% of demand spikes
    z_score_std = row['Daily_Demand_Std'] * math.sqrt(row['Lead_Time'])
    return round(service_factor * z_score_std)

stats['Optimal_Order_Quantity (EOQ)'] = stats.apply(calculate_eoq, axis=1)
stats['Safety_Stock_Level'] = stats.apply(calculate_safety_stock, axis=1)
stats['Reorder_Point'] = round((stats['Avg_Daily_Demand'] * stats['Lead_Time']) + stats['Safety_Stock_Level'])

print("\n--- Supply Chain Optimization Results ---")
print(stats[['Product', 'Optimal_Order_Quantity (EOQ)', 'Safety_Stock_Level', 'Reorder_Point']])
