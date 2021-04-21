"""Recommend global favorites

Simple solution script which scans the training data for the globally most popular items and always
recommends them, independent from the evaluation item at hand. Here, we determine popularity only
by clicks, but we could also use "basket" or "order" or a combination of these.
"""

import csv

import pandas as pd


INPUT_DIR = 'data/'
OUTPUT_DIR = 'data/'

# Read data
evaluation = pd.read_csv(INPUT_DIR + 'evaluation.csv')
transactions = pd.read_csv(INPUT_DIR + 'transactions.csv', sep='|', quoting=csv.QUOTE_NONE)

# Determine most-clicked items and add recommendations
top_items = list(transactions.groupby('itemID')['click'].sum().sort_values(ascending=False)[:5].index.values)
evaluation[[f'rec_{i + 1}' for i in range(5)]] = top_items

# Write result
evaluation.to_csv(OUTPUT_DIR + 'Jakob-global-favorites_recommendation.csv', sep='|', index=False)
