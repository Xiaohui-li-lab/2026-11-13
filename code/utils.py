"""
utils.py
Shared utilities for the replication package.
"""

import os
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')

def setup_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_table(df, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    print(f"Saved table: {path}")

def check_data_files():
    required = [
        'Inter-StateWarData_v4.0.csv',
        'NMC_Data_v6.0.csv',
        'V-Dem-CY-Core-v12.csv'
    ]
    missing = [f for f in required if not os.path.exists(os.path.join(DATA_DIR, f))]
    if missing:
        raise FileNotFoundError(
            f"Missing required data files: {missing}\n"
            "Please download them from the sources listed in README.md."
        )
