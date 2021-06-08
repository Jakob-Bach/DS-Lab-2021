"""Prepare distributed solution

Script to create comparison files and selection-template files for a distributed solution.
In contrast to the manual scoring, we don't sample items, but partition the full test set,
so each participants gets to evaluate a different subset of items. Also, participants don't award
scores, but have to tell whose team's recommendations should be selected.
"""

import csv
import pathlib

import numpy as np
import pandas as pd


SUBMISSION_DIR = pathlib.Path('data/')
DATA_DIR = pathlib.Path('data/')  # needs to contain "evaluation.csv" and "items.csv"
COMBINED_GROUPS = ['Baratheon', 'Targaryen']
NUM_PARTICIPANTS = 21


if __name__ == '__main__':
    if not DATA_DIR.exists():
        FileNotFoundError(f'"{DATA_DIR}" does not exist.')
    if not SUBMISSION_DIR.exists():
        FileNotFoundError(f'"{SUBMISSION_DIR}" does not exist.')
    test_values = pd.read_csv(DATA_DIR / 'evaluation.csv', sep='|')
    items = pd.read_csv(DATA_DIR / 'items.csv', sep='|', quoting=csv.QUOTE_NONE)
    items.rename(columns={'itemID': 'rec_item'}, inplace=True)  # for merge later
    # Read in submisson files of groups to be combined:
    submission_files = list(SUBMISSION_DIR.glob('**/*_recommendation.csv'))
    submissions = []
    for group in COMBINED_GROUPS:
        group_submission_files = [x for x in submission_files if group in x.stem]
        if len(group_submission_files) != 1:
            FileNotFoundError(f'No or multiple prediction files for group {group}.')
        submission = pd.read_csv(group_submission_files[0], sep='|', quoting=csv.QUOTE_NONE,
                                 header=0, decimal='.', encoding='utf-8', escapechar=None)
        submission['team'] = group
        submissions.append(submission)
    # Combine submissions and re-shape to enable comparison:
    comparison_table = pd.concat(submissions)
    comparison_table = comparison_table.melt(id_vars=['itemID', 'team'], value_name='rec_item',
                                             var_name='rec_nr')  # distribute recs over rows
    comparison_table['rec_nr'] = comparison_table['rec_nr'].str.replace('rec_', '')
    # Add item info for human-friendly comparison:
    comparison_table = comparison_table.merge(items)
    comparison_table.sort_values(by=['itemID', 'team', 'rec_nr'], inplace=True)
    comparison_table = test_values.merge(comparison_table)  # get original item order from test set
    item_partitioning = np.array_split(test_values['itemID'], NUM_PARTICIPANTS)
    for partition_id, partition_items in enumerate(item_partitioning):
        id_string = str(partition_id).zfill(len(str(NUM_PARTICIPANTS)))  # use leading zeros to maintain order
        comparison_table[comparison_table['itemID'].isin(list(partition_items))].to_csv(
            SUBMISSION_DIR / f'comparison_{id_string}.csv', sep='|', index=False)
        template_selection_table = pd.DataFrame({'itemID': partition_items, 'group': ''})
        template_selection_table.to_csv(SUBMISSION_DIR / f'selection_template_{id_string}.csv',
                                        sep='|', index=False)
