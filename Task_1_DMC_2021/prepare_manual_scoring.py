"""Prepare manual scoring

Script to create comparison files and scoring-template files for manual course-internal scoring.
Comparison files contain a random subset of items and show the recommendations of several teams.
To provide more context, each recommendation takes one line (instead of five recommendations per
line) and meta-data from the items file is added.
Scoring-template files contain ids of the evaluation items, team names, and scores, i.e., all
recommendations for one evaluation item and team are scored together (instead of scoring each of
the five recommendations individually).
"""

import csv
import pathlib

import pandas as pd


SUBMISSION_DIR = pathlib.Path('data/')
DATA_DIR = pathlib.Path('data/')  # needs to contain "evaluation.csv" and "items.csv"
SCORING_GROUPING = [['Arryn', 'Baratheon', 'Greyjoy'], ['Lannister', 'Targaryen', 'Tyrell']]  # which teams to compare
NUM_ITEMS = 30  # number of items to evaluate
SEED = 25  # random seed for sampling items


if __name__ == '__main__':
    test_values = pd.read_csv(DATA_DIR / 'evaluation.csv', sep='|')
    evaluation_item_ids = list(test_values['itemID'].sample(n=NUM_ITEMS, replace=False, random_state=SEED))
    items = pd.read_csv(DATA_DIR / 'items.csv', sep='|', quoting=csv.QUOTE_NONE)
    items = items[items['itemID'].isin(evaluation_item_ids)]
    items.rename(columns={'itemID': 'rec_item'}, inplace=True)  # for merge later
    submission_files = list(SUBMISSION_DIR.glob('**/*_recommendation.csv'))
    for scoring_group in SCORING_GROUPING:
        submissions = []
        for group in scoring_group:
            group_submission_files = [x for x in submission_files if group in x.stem]
            if len(group_submission_files) != 1:
                FileNotFoundError(f'No or multiple prediction files for group {group}.')
            submission = pd.read_csv(group_submission_files[0], sep='|', quoting=csv.QUOTE_NONE,
                                     header=0, decimal='.', encoding='utf-8', escapechar=None)
            submission = submission[submission['itemID'].isin(evaluation_item_ids)]
            submission['team'] = group
            submissions.append(submission)
        comparison_table = pd.concat(submissions)
        comparison_table = comparison_table.melt(id_vars=['itemID', 'team'], value_name='rec_item',
                                                 var_name='rec_nr')  # distribute recs over rows
        comparison_table['rec_nr'] = comparison_table['rec_nr'].str.replace('rec_', '')
        comparison_table = comparison_table.merge(items)
        comparison_table.sort_values(by=['itemID', 'team', 'rec_nr'], inplace=True)
        grouping_string = '_'.join(comparison_table['team'].unique())
        comparison_file_name = grouping_string + '_comparison.csv'
        comparison_table.to_csv(SUBMISSION_DIR / comparison_file_name, sep='|', index=False)
        template_scoring_table = comparison_table[['itemID', 'team']].drop_duplicates()
        template_scoring_table['scoring'] = -1
        template_scoring_file_name = grouping_string + '_scoring_template.csv'
        template_scoring_table.to_csv(SUBMISSION_DIR / template_scoring_file_name, sep='|', index=False)
