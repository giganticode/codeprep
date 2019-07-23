import logging
import logging.config
import os
import yaml

from dataprep.config import root_package_dir, version


def load_logging_config():
    path = os.path.join(root_package_dir, 'logging.yaml')
    if os.path.exists(path):
        with open(path, 'rt') as f:
            logging_config = yaml.safe_load(f.read())
        logging.config.dictConfig(logging_config)
    else:
        logging.basicConfig(level=logging.DEBUG)


load_logging_config()

logging.getLogger('matplotlib').setLevel(logging.INFO)
logging.getLogger('Ronin').setLevel(logging.INFO)

__version__ = version