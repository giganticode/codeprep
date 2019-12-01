import os

from setuptools import setup, find_packages

root_package_name = 'dataprep'


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open(os.path.join(root_package_name, 'VERSION')) as version_file:
        return version_file.read().strip()


with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()


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
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Topic :: Software Development :: Pre-processors'
      ],
      python_requires='>=3.6',
      keywords='big large data source code corpus machine learning pre-processing nlp',
      install_requires=requirements,
        entry_points={
          'console_scripts': [
              f'dataprep = {root_package_name}.__main__:main'
          ]
      },
      include_package_data=True,
      zip_safe=False)
