"""Check submission identity

Checks whether the submissions in identically-named files are actually the same. This can be used
to compare an actual submission to a reproduced submission.
"""

import csv
import pathlib

import pandas as pd


SUBMISSION_DIR_1 = pathlib.Path('data/')
SUBMISSION_DIR_2 = pathlib.Path('data/')


if __name__ == '__main__':
    if not SUBMISSION_DIR_1.exists():
        FileNotFoundError(f'"{SUBMISSION_DIR_1}" does not exist.')
    if not SUBMISSION_DIR_2.exists():
        FileNotFoundError(f'"{SUBMISSION_DIR_2}" does not exist.')
    submission_files_1 = list(SUBMISSION_DIR_1.glob('**/*_recommendation.csv'))
    submission_files_2 = list(SUBMISSION_DIR_2.glob('**/*_recommendation.csv'))
    submission_pairs = []
    for submission_file_1 in submission_files_1:
        submission_file_2 = [x for x in submission_files_2 if x.name == submission_file_1.name]
        if len(submission_file_2) > 1:
            RuntimeError('Found more than one match.')
        elif len(submission_file_2) == 1:
            submission_pairs.append((submission_file_1, submission_file_2[0]))
            submission_files_2.remove(submission_file_2[0])
        else:
            print(f'"{submission_file_1}" has no matching file.')
    for submission_file_2 in submission_files_2:
        print(f'"{submission_file_2}" has no matching file.')
    results = []
    for submission_file_1, submission_file_2 in submission_pairs:
        submission_1 = pd.read_csv(submission_file_1, sep='|', quoting=csv.QUOTE_NONE, header=0,
                                   decimal='.', encoding='utf-8', escapechar=None)
        submission_2 = pd.read_csv(submission_file_2, sep='|', quoting=csv.QUOTE_NONE, header=0,
                                   decimal='.', encoding='utf-8', escapechar=None)
        team_name = submission_file_1.stem.replace('_recommendation', '')
        num_row_diff = (submission_1 != submission_2).any(axis='columns').sum()
        num_total_diff = (submission_1 != submission_2).sum().sum()
        results.append({'Team': team_name, 'Row_diff': num_row_diff, 'Total_diff': num_total_diff})
    results = pd.DataFrame(results)
    print(results)
