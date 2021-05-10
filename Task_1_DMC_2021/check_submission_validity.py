"""Check validity of submissions

Finds all submission files named like `<<Teamname>>_recommendation.csv` in some directory and
checks their validity against an unlabeled test set ("evaluation.csv") and several formatting rules.
"""

import csv
import pathlib
from typing import Sequence

import pandas as pd


SUBMISSION_DIR = pathlib.Path('data/')
DATA_DIR = pathlib.Path('data/')  # needs to contain "evaluation.csv" and "items.csv"


def check_submission_validity(submission: pd.DataFrame, test_values: pd.DataFrame,
                              valid_itemIDs: Sequence[int]) -> str:
    if isinstance(valid_itemIDs, pd.Series):
        valid_itemIDs = list(valid_itemIDs)  # else check with .isin() might not work as expected
    if submission.shape[0] != test_values.shape[0]:
        return 'Number of recommendations wrong (might be issue with header).'
    if submission.shape[1] != 6:
        return 'Number of columns wrong (index column might be saved).'
    if list(submission) != ['itemID', 'rec_1', 'rec_2', 'rec_3', 'rec_4', 'rec_5']:
        return 'At least one column name wrong (might be quoted).'
    if (submission.dtypes != 'int64').any():
        return 'At least one itemID is not an integer.'
    if submission.isna().any().any():
        return 'At least one NA.'
    if sorted(submission['itemID']) != sorted(test_values['itemID']):
        return 'At least one recommendation for a wrong itemID.'
    if not submission[[f'rec_{i}' for i in range(1, 6)]].isin(valid_itemIDs).all().all():
        return 'At least one non-existing itemID recommended.'
    if (submission['itemID'] != test_values['itemID']).any():
        return 'Order of itemID changed, else valid.'
    return 'Valid.'


if __name__ == '__main__':
    items = pd.read_csv(DATA_DIR / 'items.csv', sep='|', quoting=csv.QUOTE_NONE)
    test_values = pd.read_csv(DATA_DIR / 'evaluation.csv', sep='|', quoting=csv.QUOTE_NONE)
    submission_files = SUBMISSION_DIR.glob('**/*_recommendation.csv')
    results = []
    for submission_file in submission_files:
        submission = pd.read_csv(submission_file, sep='|', quoting=csv.QUOTE_NONE, header=0,
                                 decimal='.', encoding='utf-8', escapechar=None)
        team_name = submission_file.stem.replace('_recommendation', '')
        validity_status = check_submission_validity(submission=submission, test_values=test_values,
                                                    valid_itemIDs=items['itemID'])
        results.append({'Team': team_name, 'Validity': validity_status})
    results = pd.DataFrame(results)
    print(results)
