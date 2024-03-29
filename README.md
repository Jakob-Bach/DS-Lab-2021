# Data Science Laboratory Course 2021

This is the supervisor repo of the ["Data Science Laboratory Course"](https://dbis.ipd.kit.edu/english/3044.php) at KIT in 2021.
Students worked on two subtasks:

- the [Data Mining Cup 2021](https://www.data-mining-cup.com/dmc-2021/)
- a research dataset, created from verification of auction process models

The repo provides files for preparing the datasets, some basic exploration, course-internal splitting, scoring, and demo submissions for that.

## Setup

We use Python with version `3.9.2`.
We recommend to set up a virtual environment to install the dependencies, e.g., with `virtualenv`:

```bash
python -m virtualenv -p <path/to/right/python/executable> <path/to/env/destination>
```

or with `conda` (which we used, version `4.10.0`):

```bash
conda create --name ds-lab-2021 python=3.9.2
```

Next, install the dependencies with

```bash
python -m pip install -r requirements.txt
```

If you make changes to the environment and you want to persist them, run

```bash
python -m pip freeze > requirements.txt
```

We installed `spyder-kernels` into the environment, so you should be able to use the environment in the IDE `Sypder`
(if the versions of `spyder-kernels` and `Spyder` are compatible).

## Task 1: Data Mining Cup 2021 (`Task_1_DMC_2021/`)

### Preparation

Download the DMC task from the [website](https://www.data-mining-cup.com/dmc-2021/).
Place the three CSVs in a folder called `data` in the folder `Task_1_DMC_2021`.

### Exploration

`explore_data.py` allows very basic interactive (e.g., in IDE) exploration.

### Scoring

- `check_submission_validity.py` checks whether submission files have the right format.
- `check_submission_identity.py` checks whether identically-named submission files have the same content (= checks reproducibility).
- `prepare_manual_scoring.py` prepares input files and output files for manual course-internal scoring of randomly sampled recommendations.
- `evaluate_manual_scoring.py` reads output files of manual scoring and combines them.

### Demo Submissions

We provide two simple demo submission scripts that produce solutions observing the DMC submission format:

- `recommend_global_favorites.py`: Ignore item to evaluate and recommend globally popular items.
- `recommend_cooccurring_favorites.py`: Find items which are most popular in sessions with item to evaluate.

### Distributed Submission

For the DMC submission, we combine multiple submissions that were created by the teams' pipelines.
To this end, we let the participants manually decide which of the submissions to use for each item.
As making this decision for the full test set would require a lot of effort, we distribute the manual work over all participants.

- `prepare_distributed_solution.py` prepares input files and output files for the manual selection process.
- `combine_distributed_solution.py` read output files of manual selection as well as submission files and combines them.

## Task 2: Verification of Auction Process Models (`Task_2_Auction_Verification/`)

For some background on the scenario, you can read

> Ordoni, E., Mülle, J., & Böhm, K. (2020). Verification of Data-Value-Aware Processes and a Case Study on Spectrum Auctions.

Our datasets are based on verification of process models mimicking the German 4G Spectrum Auction,
featuring six products and four bidders.
We have two datasets, which have nearly the same columns, but differ in the domain of their data values.
I.e., one dataset has a higher range of prices than the other one and therefore has more data objects.
Also, the interpretation of the formula (= property) to be verified is slightly different between the two dataset.
In the smaller dataset (`auction_verification`), each price is encoded as a separate data value.
In the larger dataset (`auction_verification_large`), prices are encoded binarily, which results in longer formulas.

## Preparation

Obtain the raw small dataset `Process4.csv` and the raw partititions of the large dataset `result[0-6].csv`.
Place them a folder called `data` in the folder `Task_2_Auction_Verification`.
Run `prepare_data.py` to create student-friendly, pre-processed versions of the datasets.

## Exploration

`explore_data.py` allows basic interactive (e.g., in IDE) exploration and predictions.
