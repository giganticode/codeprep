import os

from setuptools import setup, find_packages

root_package_name = 'dataprep'


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open(os.path.join(root_package_name, 'VERSION')) as version_file:
        return version_file.read().strip()


setup(name='giganticode-dataprep',
      version=version(),
      description='A toolkit for pre-processing large source code corpora',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='http://github.com/giganticode/dataprep',
      author='giganticode',
      author_email='hlibbabii@gmail.com',
      license='MIT',
      packages=find_packages(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Operating System :: POSIX :: Linux',
          'Topic :: Software Development :: Pre-processors'
      ],
      python_requires='>=3.6',
      keywords='big large data source code corpus machine learning pre-processing nlp',
      install_requires=[
          'appdirs==1.4.3',
          'coverage==4.5.3',
          'dill==0.2.9',
          'docopt==0.6.2',
          'docopt-subcommands==3.0.0',
          'jsons==0.8.3',
          'matplotlib==3.0.3',
          'nltk==3.4.4',
          'Pygments==2.3.1',
          'PyYAML==5.1',
          'regex==2019.3.12',
          'tqdm==4.31.1',
      ],
        entry_points={
          'console_scripts': [
              f'dataprep = {root_package_name}.__main__:main'
          ]
      },
      include_package_data=True,
      zip_safe=False)
