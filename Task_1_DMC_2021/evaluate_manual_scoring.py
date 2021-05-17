"""Evaluate manual scoring

Reads manual scoring files having the format from "prepare_manual_scoring.py", checks their validity,
and combines them to compute avergae scores.
"""

import csv
import pathlib
from typing import Optional

import pandas as pd

import prepare_manual_scoring


SUBMISSION_DIR = pathlib.Path('data/')


# Return None if valid
def check_scoring_validity(scoring_table: pd.DataFrame) -> Optional[str]:
    if scoring_table.shape[1] != 3:
        return 'Number of columns wrong (index column might be saved).'
    if list(scoring_table) != ['itemID', 'team', 'scoring']:
        return 'At least one column name wrong (might be quoted).'
    if (scoring_table.groupby(['itemID', 'team']).size() != 1).any():
        return 'Multiple scores for at least one item-team combination.'
    if (scoring_table.groupby('team').size() != prepare_manual_scoring.NUM_ITEMS).any():
        return 'Invalid number of scores for at least one team.'
    if scoring_table.isna().any().any():
        return 'At least one NA.'
    if (scoring_table.groupby('itemID')['scoring'].nunique() != scoring_table['team'].nunique()).any():
        return 'At least one items has not the right number of distinct scores.'
    if sorted(scoring_table['scoring'].unique()) != [0, 1, 2]:
        return 'At least one score out of range.'
    return None


if __name__ == '__main__':
    if not SUBMISSION_DIR.exists():
        FileNotFoundError(f'"{SUBMISSION_DIR}" does not exist.')
    scoring_files = SUBMISSION_DIR.glob('**/*_scoring.csv')
    scoring_tables = []
    for scoring_file in scoring_files:
        scoring_table = pd.read_csv(scoring_file, sep='|', quoting=csv.QUOTE_NONE, header=0,
                                    decimal='.', encoding='utf-8', escapechar=None)
        validity_result = check_scoring_validity(scoring_table)
        if validity_result is not None:
            print(f'Scoring file "{scoring_file.stem}" is invalid because "{validity_result}", ' +
                  'will be ignored.')
            continue
        scoring_tables.append(scoring_table)
    scoring_table = pd.concat(scoring_tables)
    print(scoring_table.groupby('team')['scoring'].mean().sort_values(ascending=False).to_frame())
