from setuptools import setup, find_packages

from dataprep.config import version, app_name


def readme():
    with open('README.md') as f:
        return f.read()


setup(name=app_name,
      version=version,
      description='A toolkit for pre-processing large source code corpora',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='http://github.com/giganticode/dataprep',
      author='giganticode',
      author_email='hlibbabii@gmail.com',
      license='MIT',
      packages=find_packages(),
      # scripts=['bin/run'],
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
          'docopt',
          'jsons',
          'regex',
          'tqdm',
          'appdirs'
      ],
        entry_points={
          'console_scripts': [
              'dataprep = dataprep.__main__:main'
          ]
      },
      include_package_data=True,
      zip_safe=False)