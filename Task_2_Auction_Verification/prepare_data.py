"""Prepare auction-verification data

Script which prepares the dataset for the practical course by:
    - using NAs instead of zeros where appropriate
    - re-naming and re-ordering existing columns
    - creating new columns from a former string column describing the allocation
    - adding the ids of the current product permutation and iteration
"""

import pandas as pd


INPUT_PATH = 'data/Process4.csv'
OUTPUT_PATH = 'data/auction_verification.csv'

dataset = pd.read_csv(INPUT_PATH)

# Replace numeric placeholders with proper NaNs (after making sure a nullable int type is used):
dataset[['winner', 'revenue']] = dataset[['winner', 'revenue']].astype('Int64').replace(0, float('nan'))
# Use more intutive column names, which also group columns logically:
dataset.rename(columns={
    'property': 'property.formula', 'id': 'property.product', 'winner': 'property.winner',
    'lowestprice': 'property.price', 'capB1': 'process.b1.capacity', 'capB2': 'process.b2.capacity',
    'capB3': 'process.b3.capacity', 'capB4': 'process.b4.capacity', 'revenue': 'allocation.revenue',
    'last round': 'verification.is_final', 'result': 'verification.result', 'time': 'verification.time',
    'marking': 'verification.markings', 'edges': 'verification.edges'
}, inplace=True)
# Extract numeric values out of final-allocation string:
dataset['final allocation'].fillna('', inplace=True)
for i in range(1, 7):
    dataset[[f'allocation.p{i}.price', f'allocation.p{i}.winner']] = dataset['final allocation'].str.extract(
        f'product{i}:  price (\\d) winner (\\d)').astype(float).astype('Int64')
dataset.drop(columns='final allocation', inplace=True)
# Identify product permutations and the iterations within each permutation setting:
dataset['id.product_permutation'] = dataset['verification.is_final'].shift(fill_value=True).cumsum()
dataset['id.iteration'] = dataset.groupby('id.product_permutation').cumcount() + 1
# Re-order columns
dataset = dataset[[x for x in dataset.columns if x.startswith('id')] +
                  [x for x in dataset.columns if x.startswith('process')] +
                  [x for x in dataset.columns if x.startswith('property')] +
                  [x for x in dataset.columns if x.startswith('verification')] +
                  [x for x in dataset.columns if x.startswith('allocation')]]

dataset.to_csv(OUTPUT_PATH, index=False)
