"""Explore auction-verification data

Code snippets for interactively (e.g., in an IDE) exploring the data, including simple predictions.
Not intended for execution from a console.
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sklearn.model_selection
import sklearn.tree
import tqdm


dataset = pd.read_csv('data/auction_verification.csv')
# Type is not properly recognized for all columns:
float_cols = dataset.dtypes[dataset.dtypes == 'float'].index
dataset[float_cols] = dataset[float_cols].astype('Int64')

# -----Exploration-----

# ---Basic properties----
summary_table = dataset.describe()
dataset.nunique()
dataset.isna().sum()

# ---Distribution of individual features---
dataset['allocation.revenue'].value_counts()
dataset['verification.is_final'].value_counts()
dataset['verification.result'].value_counts()
dataset['verification.time'].plot.hist()

# ---Relationship between features---
# Number of capacity combinations:
dataset.groupby([x for x in dataset.columns if 'capacity' in x]).ngroups
# In first iteration of each verification sequence, capacity is always same:
dataset.loc[dataset['id.iteration'] == 1, [x for x in dataset.columns if 'capacity' in x]].nunique()
# In last iteration of each verification sequence, five of ten products are assigned (the last
# product would affect capacity only in next iteration):
(dataset.groupby('id.product_permutation').last()[[x for x in dataset.columns if 'capacity' in x]].sum(axis='columns') == 5).all()
# Allocation is set only in last round:
(dataset['allocation.p1.price'].notna() == dataset['verification.is_final']).all()
(dataset['allocation.revenue'].notna() == dataset['verification.is_final']).all()
# Number of wins is lower than the capacities:
initial_capacities = dataset.loc[0, [x for x in dataset.columns if 'capacity' in x]]
for i in range(1, 5):
    print(((dataset[[x for x in dataset.columns if 'allocation' in x and 'winner' in x]] == i).sum(
        axis='columns') <= initial_capacities.iloc[i - 1]).all())
# Check maxmimum prices for each product and bidder (might be NaN if bidder never wins product):
for product_id in range(1, 7):
    for bidder_id in range(1, 5):
        print(f'b{bidder_id}.p{product_id}.max_price:',
              dataset.loc[dataset[f'allocation.p{product_id}.winner'] == bidder_id,
                          f'allocation.p{product_id}.price'].max())
    print()
# For each permutation of products and for each product within the permutation, there are two
# positive results (determine price and determine winner):
(dataset.groupby(['id.product_permutation', 'property.product'])['verification.result'].sum() == 2).all()
# If last iteration, result is true
pd.crosstab(dataset['verification.is_final'], dataset['verification.result'])
# If bidder 3 wins, result is true (because there is no bidder left which could win instead):
pd.crosstab(dataset['property.winner'] == 3, dataset['verification.result'])
# Correlation:
plt.figure(figsize=(7, 7))
sns.heatmap(dataset[dataset.columns[dataset.notna().all()]].corr(), fmt='.2f', vmin=-1, vmax=1,
            cmap='PRGn', annot=True, square=True, cbar=False)


# ----Regression-----

features = [x for x in dataset.columns if x.startswith('pro') and x != 'property.formula']
# Different splits possible, e.g., random, based on permutations or based on capacity settings:
# cv = sklearn.model_selection.KFold(n_splits=10, shuffle=True, random_state=25)
# splits = cv.split(X=dataset)
cv = sklearn.model_selection.LeaveOneGroupOut()
splits = cv.split(X=dataset, groups=dataset['id.product_permutation'])
# splits = cv.split(X=dataset, groups=dataset.groupby([x for x in dataset.columns if 'capacity' in x]).ngroup())
results = []
for fold_idx, (train_idx, test_idx) in tqdm.tqdm(enumerate(splits)):
    X_train = dataset.loc[train_idx, features].fillna(0)
    y_train = dataset.loc[train_idx, 'verification.time'].astype(float)
    X_test = dataset.loc[test_idx, features].fillna(0)
    y_test = dataset.loc[test_idx, 'verification.time'].astype(float)
    model = sklearn.tree.DecisionTreeRegressor(random_state=25)  # max_depth=3
    model.fit(X_train, y_train)
    train_r2 = sklearn.metrics.r2_score(y_true=y_train, y_pred=model.predict(X_train))
    test_r2 = sklearn.metrics.r2_score(y_true=y_test, y_pred=model.predict(X_test))
    result = {'fold': fold_idx, 'train_r2': train_r2, 'test_r2': test_r2}
    results.append(result)
pd.DataFrame(results).describe()

pd.Series(model.feature_importances_, X_train.columns).plot.bar()
sklearn.tree.plot_tree(model, feature_names=X_train.columns)  # max_depth=3
plt.savefig('data/regression_tree.pdf')


# ----Classification-----

features = [x for x in dataset.columns if x.startswith('pro') and x != 'property.formula']
# Different splits possible, e.g., random, based on permutations or based on capacity settings:
# cv = sklearn.model_selection.KFold(n_splits=10, shuffle=True, random_state=25)
# splits = cv.split(X=dataset)
cv = sklearn.model_selection.LeaveOneGroupOut()
splits = cv.split(X=dataset, groups=dataset['id.product_permutation'])
# splits = cv.split(X=dataset, groups=dataset.groupby([x for x in dataset.columns if 'capacity' in x]).ngroup())
results = []
for fold_idx, (train_idx, test_idx) in tqdm.tqdm(enumerate(splits)):
    X_train = dataset.loc[train_idx, features].fillna(0)
    y_train = dataset.loc[train_idx, 'verification.result']
    X_test = dataset.loc[test_idx, features].fillna(0)
    y_test = dataset.loc[test_idx, 'verification.result']
    model = sklearn.tree.DecisionTreeClassifier(random_state=25)  # max_depth=3
    model.fit(X_train, y_train)
    train_mcc = sklearn.metrics.matthews_corrcoef(y_true=y_train, y_pred=model.predict(X_train))
    test_mcc = sklearn.metrics.matthews_corrcoef(y_true=y_test, y_pred=model.predict(X_test))
    result = {'fold': fold_idx, 'train_mcc': train_mcc, 'test_mcc': test_mcc}
    results.append(result)
pd.DataFrame(results).describe()

pd.Series(model.feature_importances_, X_train.columns).plot.bar()
sklearn.tree.plot_tree(model, feature_names=X_train.columns)  # max_depth=3
plt.savefig('data/classification_tree.pdf')
