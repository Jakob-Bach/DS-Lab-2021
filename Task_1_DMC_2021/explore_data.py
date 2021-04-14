"""Explore data

Code snippets for interactively (e.g., in an IDE) exploring the data. Not optimized for sequential
execution on a console (and Jakob was too lazy to create a notebook with textual interpretation).
"""

import csv

import pandas as pd


# Load data
# unnecessary options (default or recognized): header=True, decimal='.', encoding='utf-8', escapechar=None
evaluation = pd.read_csv('data/evaluation.csv')
items = pd.read_csv('data/items.csv', sep='|', quoting=csv.QUOTE_NONE)
transactions = pd.read_csv('data/transactions.csv', sep='|')
assert len(evaluation) == 1000  # compare to number of lines in file (minus header)
assert len(items) == 78334
assert len(transactions) == 365143

# Expore "items"
items.head()
items.dtypes
items.nunique()
assert items['itemID'].nunique() == len(items)  # check id
items.groupby('title').size().value_counts()  # .plot.bar()
items.groupby('author').size().value_counts()
items.groupby('publisher').size().value_counts()
items.groupby('main topic').size().value_counts()
items.groupby('subtopics').size().value_counts()

# Explore "transactions"
transactions.head()
transactions.dtypes
transactions.nunique()
assert len(transactions.groupby(['sessionID', 'itemID']).size().value_counts()) == 1  # check id
transactions.groupby('sessionID').size().value_counts()
transactions.groupby('itemID').size().value_counts()
transactions.drop(columns=['itemID', 'sessionID']).describe()
transactions.groupby('click').size()
transactions.groupby('basket').size()
transactions.groupby('order').size()

# Explore "evaluation"
evaluation.head()
assert evaluation['itemID'].nunique() == len(evaluation)  # check that only distinct item ids
evaluation['itemID'].isin(transactions['itemID']).value_counts()  # check whether items occur in training data
