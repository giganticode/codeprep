# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import os

from setuptools import setup, find_packages

root_package_name = 'codeprep'


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open(os.path.join(root_package_name, 'VERSION')) as version_file:
        return version_file.read().strip()


with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()


setup(name='giganticode-codeprep',
      version=version(),
      description='A toolkit for pre-processing large source code corpora',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='http://github.com/giganticode/codeprep',
      author='Hlib Babii',
      author_email='hlibbabii@gmail.com',
      license='Apache-2.0',
      packages=find_packages(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Topic :: Software Development :: Pre-processors'
      ],
      python_requires='>=3.6',
      keywords='big large data source code corpus machine learning pre-processing nlp',
      install_requires=requirements,
        entry_points={
          'console_scripts': [
              f'codeprep = {root_package_name}.__main__:main'
          ]
      },
      include_package_data=True,
      zip_safe=False)