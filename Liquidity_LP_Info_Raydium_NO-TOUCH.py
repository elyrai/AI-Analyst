
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 18:28:54 2024

@author: antoinepury
"""

import requests
import csv
from datetime import datetime

# API URLs
pool_info_url = "https://api-v3.raydium.io/pools/line/liquidity?id=9Tb2ohu5P16BpBarqd3N27WnkF51Ukfs8Z1GzzLDxVZW"

# Output CSV file
output_csv = "raydium_liquidity_data_SOL-GOAT.csv"

# Fetch the data from the API
response = requests.get(pool_info_url, headers={'accept': 'application/json'})
if response.status_code == 200:
    data = response.json()
    if data.get("success"):
        liquidity_data = data.get("data", {}).get("line", [])
        
        # Save data to CSV
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(["Time (UTC)", "Liquidity"])
            
            # Write data rows
            for entry in liquidity_data:
                time_utc = datetime.utcfromtimestamp(entry["time"]).strftime('%Y-%m-%d %H:%M:%S')
                liquidity = entry["liquidity"]
                writer.writerow([time_utc, liquidity])
        
        print(f"Data saved successfully to {output_csv}")
    else:
        print("API call succeeded, but no data found.")
else:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")