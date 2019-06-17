from dataprep.api import nosplit
from dataprep.api import chars
from dataprep.api import basic
from dataprep.api import basic_with_numbers
from dataprep.api import bpe
from dataprep.api import ronin

import logging
import logging.config
import os
import yaml

from dataprep.config import root_package_dir


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