from dataprep import parse_projects, to_repr
from dataprep.dataset import Dataset


def run_parsing(dataset: Dataset) -> None:
    if not dataset.parsed.ready():
        parse_projects.run(dataset)
    elif not dataset.parsed.is_up_to_date():
        dataset.parsed.archive()
        parse_projects.run(dataset)
    else:
        print("Parsed dataset is up-to-date.")


def run_preprocessing(dataset: Dataset) -> None:
    print("Stage 1/2: Parsing...")
    run_parsing(dataset)
    print("Stage 2/2. Preprocessing...")
    to_repr.run(dataset)


def run_all(dataset: Dataset) -> None:
    if not dataset.preprocessed.ready():
        run_preprocessing(dataset)
    elif dataset.preprocessed.is_up_to_date():
        print(f"Dataset is already preprocessed at: {dataset.preprocessed.path}")
        exit(0)
    else:
        dataset.preprocessed.archive()
        run_preprocessing(dataset)
    print(f"The preprocessed dataset is at {dataset.preprocessed.path}")