"""This module runs different stages of preprocessing flow and makes sure not to rerun a stage if its results are already available.
"""
from dataprep import parse_projects, to_repr
from dataprep.dataset import Dataset


def run_parsing(dataset: Dataset) -> None:
    print("--- Parsing...")
    if not dataset.parsed.ready():
        parse_projects.run(dataset)
    elif dataset.parsed.is_outdated():
        dataset.parsed.archive()
        parse_projects.run(dataset)
    else:
        print("Parsed dataset is up-to-date.")


def run_until_preprocessing(dataset: Dataset) -> None:
    run_parsing(dataset)
    print("--- Preprocessing...")
    if not dataset.preprocessed.ready():
        to_repr.run(dataset)
    elif dataset.preprocessed.is_outdated():
        dataset.preprocessed.archive()
        to_repr.run(dataset)
    else:
        print(f"Dataset is already preprocessed and up-to-date.")
