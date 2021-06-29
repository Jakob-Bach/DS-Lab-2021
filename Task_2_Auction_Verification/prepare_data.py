"""Prepare auction-verification data

Script which prepares the datasets for the practical course by:
    - using NAs instead of zeros where appropriate
    - re-naming and re-ordering existing columns
    - creating new columns from a former string column describing the allocation
    - adding the ids of the current product permutation and iteration

For the large dataset,
    - add two further ids
    - make winner column consistent to small dataset
    - make capacities in rows with known winner consistent to small dataset
"""

import pandas as pd


# If entry of "INPUT_PATHS" is a list, these datasets will be merged
INPUT_PATHS = ['data/Process4.csv', [f'data/result{i}.csv' for i in range(6)]]
OUTPUT_PATHS = ['data/auction_verification.csv', 'data/auction_verification_large.csv']


# Conduct various pre-processing steps and return pre-processed dataset.
def preprocess_dataset(dataset: pd.DataFrame) -> pd.DataFrame():
    dataset = dataset.copy()
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
        # why "[ ]?" -> in some datasets there is an additional whitespace in the string, in others not
        dataset[[f'allocation.p{i}.price', f'allocation.p{i}.winner']] = dataset['final allocation'].str.extract(
            f'product{i}: [ ]?price ([0-9]+) winner ([0-9])').astype(float).astype('Int64')
    dataset.drop(columns='final allocation', inplace=True)
    if dataset['property.price'].max() < 10:  # small-domain dataset
        # Identify product permutations and the iterations within each permutation setting:
        dataset['id.product_permutation'] = dataset['verification.is_final'].shift(fill_value=True).cumsum()
        dataset['id.iteration'] = dataset.groupby('id.product_permutation').cumcount() + 1
    else:  # large-domain dataset
        # Extract winner from binary encoding (wasn't done in dataset for rows with result == false):
        dataset.loc[dataset['property.formula'].str.contains('winner_1_1 > 0 AND winner_2_0 > 0 AND winner_4_0 > 0'),
                    'property.winner'] = 1
        dataset.loc[dataset['property.formula'].str.contains('winner_1_0 > 0 AND winner_2_1 > 0 AND winner_4_0 > 0'),
                    'property.winner'] = 2
        dataset.loc[dataset['property.formula'].str.contains('winner_1_1 > 0 AND winner_2_1 > 0 AND winner_4_0 > 0'),
                    'property.winner'] = 3
        dataset.loc[dataset['property.formula'].str.contains('winner_1_0 > 0 AND winner_2_0 > 0 AND winner_4_1 > 0'),
                    'property.winner'] = 4
        # Do not reduce capacity already in rows where winner is sucessfully determined:
        for bidder in range(1, 5):
            dataset[f'process.b{bidder}.capacity'] += dataset['verification.result'] &\
                (dataset['property.winner'] == bidder).fillna(False)
        # Identify product permutations and the iterations within each permutation setting:
        dataset['id.product_permutation'] =\
            (dataset['property.winner'].isna() & dataset['property.winner'].shift(fill_value=0).notna() &
             (dataset['process.b1.capacity'] == 2) & (dataset['process.b2.capacity'] == 3) &
             (dataset['process.b3.capacity'] == 2) & (dataset['process.b4.capacity'] == 1)).cumsum().astype('Int64')
        dataset['id.iteration'] = dataset.groupby('id.product_permutation').cumcount() + 1
        # Identify product position within each permutation setting:
        dataset['new_product'] = (dataset['property.product'] != dataset['property.product'].shift(fill_value=0)) |\
            (dataset['id.product_permutation'] != dataset['id.product_permutation'].shift(fill_value=0))
        dataset['id.product_position'] = dataset.groupby(['id.product_permutation'])['new_product'].cumsum()
        dataset.drop(columns='new_product', inplace=True)
        # Identify parallel cases for each product within a permutation:
        dataset['after_winner'] = dataset['property.winner'].isna() &\
            dataset['property.winner'].shift(fill_value=0).notna()
        dataset['id.product_case'] = dataset.groupby(
            ['id.product_permutation', 'property.product'])['after_winner'].cumsum()
        dataset.drop(columns='after_winner', inplace=True)
    # Re-order columns
    dataset = dataset[[x for x in dataset.columns if x.startswith('id')] +
                      [x for x in dataset.columns if x.startswith('process')] +
                      [x for x in dataset.columns if x.startswith('property')] +
                      [x for x in dataset.columns if x.startswith('verification')] +
                      [x for x in dataset.columns if x.startswith('allocation')]]
    return dataset


assert len(INPUT_PATHS) == len(OUTPUT_PATHS)
for input_path, output_path in zip(INPUT_PATHS, OUTPUT_PATHS):
    if isinstance(input_path, list):
        dataset = pd.concat([pd.read_csv(x) for x in input_path], ignore_index=True)
    else:
        dataset = pd.read_csv(input_path)
    dataset = preprocess_dataset(dataset)
    dataset.to_csv(output_path, index=False)
