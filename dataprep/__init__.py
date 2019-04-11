from dataprep.api import nosplit
from dataprep.api import chars
from dataprep.api import basic
from dataprep.api import basic_with_numbers
from dataprep.api import bpe

import logging
import logging.config
import os
import yaml

from dataprep.config import root_package_dir

path = os.path.join(root_package_dir, 'logging.yaml')
if os.path.exists(path):
    with open(path, 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
else:
    logging.basicConfig(level=logging.DEBUG)