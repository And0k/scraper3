"""A setuptools based setup module.
"""
from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
OSI_license = 'GNU General Public License v3 or later (GPLv3+)'
setup(
    name='scrxPDF',
    version='0.0.1',

    description='Extracts data from Monthly Production Reports *.pdf to *.csv file(s)',
    long_description=long_description,

    url='https://github.com/pypa/sampleproject',
    author='Andrey Korzh',
    author_email='ao.korzh@gmail.com',

    license=OSI_license,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: ' + OSI_license,
        'Environment :: Console',
        'Programming Language :: Python :: 3',
    ],

    keywords='scraping',

    python_requires='>=3',
    # Managing python package versions in scm metadata instead of 
    # declaring them as the version argument or in a scm managed file
    use_scm_version = {"root": "..", "relative_to": __file__},
    setup_requires = ['setuptools_scm'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['future'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'sample': ['package_data.dat'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },
)
