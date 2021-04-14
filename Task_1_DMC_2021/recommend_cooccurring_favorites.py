"""Recommend co-occuding favorites

Simple solution script which scans the training data for all transactions containing the evaluation
item at-hand and recommnends the most popular co-occurrring items. Defaults to the globally
most popular items if the item-at-hand does not occur in the training data. We determine popularity
only by clicks, but we could also use "basket" or "order" or a combination of these.
"""

import csv

import pandas as pd


INPUT_DIR = 'data/'
OUTPUT_DIR = 'data/'

# Read data
evaluation = pd.read_csv(INPUT_DIR + 'evaluation.csv')
transactions = pd.read_csv(INPUT_DIR + 'transactions.csv', sep='|', quoting=csv.QUOTE_NONE)

# Determine defaults
global_item_ranking = transactions.groupby('itemID')['click'].sum().sort_values(ascending=False)
global_top_items = list(global_item_ranking[:5].index.values)

# Add recommendations
evaluation[[f'rec_{i + 1}' for i in range(5)]] = None  # initialize empty columns
for i, itemID in enumerate(evaluation['itemID']):
    relevant_sessions = transactions.loc[transactions['itemID'] == itemID, 'sessionID']
    if len(relevant_sessions) == 0:  # item not in training data
        evaluation.iloc[i, 1:] = global_top_items
    else:
        relevant_data = transactions[transactions['sessionID'].isin(relevant_sessions) &
                                     (transactions['itemID'] != itemID)]
        relevant_item_ranking = relevant_data.groupby('itemID')['click'].sum().sort_values(ascending=False)
        top_items = list(relevant_item_ranking[:5].index.values)
        if len(top_items) < 5:  # if not co-occurring items, fill with globally popular items
            top_items.extend(global_top_items[:(5 - len(top_items))])
        evaluation.iloc[i, 1:] = top_items

# Write result
evaluation.to_csv(OUTPUT_DIR + 'prediction.csv', sep='|', index=False)
