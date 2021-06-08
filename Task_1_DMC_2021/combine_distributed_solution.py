"""Combine distributed solution

Script that first reads in manually filled-out selection files, having the format defined by
"prepare_distributed_solution.py". Selection files tell whose team's solution to use for each item.
Next, we read in the the automatically created recommendations of the teams and combine them based
on the manual input.
"""


import csv
import pathlib

import numpy as np
import pandas as pd

import check_submission_validity


SUBMISSION_DIR = pathlib.Path('data/')
DATA_DIR = pathlib.Path('data/')  # needs to contain "evaluation.csv"
COMBINED_GROUPS = ['Baratheon', 'Targaryen']


if __name__ == '__main__':
    if not DATA_DIR.exists():
        FileNotFoundError(f'"{DATA_DIR}" does not exist.')
    if not SUBMISSION_DIR.exists():
        FileNotFoundError(f'"{SUBMISSION_DIR}" does not exist.')
    test_values = pd.read_csv(DATA_DIR / 'evaluation.csv', sep='|')
    # Read in manual selections:
    selection_files = SUBMISSION_DIR.glob('**/selection_*.csv')
    selection_tables = []
    for selection_file in selection_files:
        selection_table = pd.read_csv(selection_file, sep='|', quoting=csv.QUOTE_NONE, header=0,
                                      decimal='.', encoding='utf-8', escapechar=None)
        if not selection_table['group'].isin(COMBINED_GROUPS).all():
            print(f'Selection file "{selection_file.stem}" contains invalid group names.')
        selection_tables.append(selection_table)
    selection_table = pd.concat(selection_tables)
    # Read in submissions (recommendations) and extract those parts were they are best accordng
    # to the manual selections:
    submission = pd.DataFrame({'itemID': test_values['itemID']})
    submission[[f'rec_{i + 1}' for i in range(5)]] = -1
    submission_files = list(SUBMISSION_DIR.glob('**/*_recommendation.csv'))
    for group in COMBINED_GROUPS:
        group_submission_files = [x for x in submission_files if group in x.stem]
        if len(group_submission_files) != 1:
            FileNotFoundError(f'No or multiple prediction files for group {group}.')
        group_submission = pd.read_csv(group_submission_files[0], sep='|', quoting=csv.QUOTE_NONE,
                                       header=0, decimal='.', encoding='utf-8', escapechar=None)
        select_group_idx = np.where(selection_table['group'] == group)[0]
        submission.iloc[select_group_idx, 1:] = group_submission.iloc[select_group_idx, 1:]
    # Check and save final submission:
    print(check_submission_validity.check_submission_validity(
        submission=submission, test_values=test_values, valid_itemIDs=test_values['itemID']))
    submission.to_csv(SUBMISSION_DIR / 'IT_Karlsruhe_1.csv', index=False)
