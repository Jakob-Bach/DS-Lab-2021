# Data Science Laboratory Course 2021

This is the supervisor repo of the ["Data Science Laboratory Course"](https://dbis.ipd.kit.edu/english/3044.php) at KIT in 2021.
Students worked on two subtasks:

- the [Data Mining Cup 2021](https://www.data-mining-cup.com/dmc-2021/)
- a research task

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

### Data Exploration

`explore_data.py` allows very basic interactive (e.g., in IDE) exploration.

### Internal Scoring

`check_validity.py` checks whether submission files have the right format.

### Demo Submissions

We provide two simple demo submission scripts that produce solutions observing the DMC submission format:

- `recommend_global_favorites.py`: Ignore item to evaluate and recommend globally popular items.
- `recommend_cooccurring_favorites.py`: Find items which are most popular in sessions with item to evaluate.
