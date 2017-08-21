# -*- coding: utf-8 -*-

# relimport.py is a very simple script that tests importing using relative
# imports (available in Python 2.5 and up)
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python
from setuptools import find_packages
from cx_Freeze import setup, Executable

executables = [
    Executable('scrxPDF1707.py')
]

setup(
	name='scrxPDF',
    version='0.0.1',
	description='Extracts data from Monthly Production Reports *.pdf to *.csv file(s)',
    executables=executables,
    keywords='scraping',

    python_requires='>=3',
    # Managing python package versions in scm metadata instead of 
    # declaring them as the version argument or in a scm managed file
    use_scm_version=True,
    setup_requires=['setuptools_scm'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    )