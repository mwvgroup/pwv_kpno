#!/usr/bin/env python3
import os
import re
from setuptools import setup


def long_description():
    with open('README.md') as ofile:
        readme = ofile.read()

        # Get the Package Description section
        description = readme.split('## 1) Package Description')[-1]
        description = description.split('#')[0]

        # Remove markdown links
        description = re.sub("\]\(([\s\S]*?)\)", "", description).strip('\n')
        description = description.replace('[', '').replace(']', '')
        return description


def add_data_files(file_list, directory, ext_tuple):
    """List the contents of a directory

    Walk through a directory and create a list of encountered file paths.
    Only include files with extensions contained in a tuple argument.

    Args:
        directory (str)  : A directory to walk through.
        ext_tuple (tuple): A tuple of file extensions.

    Returns:
        A list of file paths.
    """

    pattern = re.compile('(.*(({})$))'.format('|'.join(ext_tuple)))
    files = [os.path.join(directory, fname)
             for fname in os.listdir(os.path.join('pwv_kpno', directory))
             if pattern.search(fname)]
    file_list.extend(files)


DATA_FILES = ['CONFIG.txt']
add_data_files(DATA_FILES, 'atm_models', ('.csv',))
add_data_files(DATA_FILES, 'pwv_tables', ('.csv',))
add_data_files(DATA_FILES, 'sims_phosim/data/atmosphere', ('.txt.',))
add_data_files(DATA_FILES, 'suomi_data', ('.plot',))

setup(name='pwv_kpno',
      version='0.9.10',
      packages=['pwv_kpno'],
      keywords='KPNO atmospheric transmission PWV precipitable water vapor',
      description='Models the atmospheric transmission function for KPNO',
      long_description=long_description(),
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Scientific/Engineering :: Atmospheric Science',
                   'Topic :: Scientific/Engineering :: Physics'],

      author='Daniel Perrefort',
      author_email='djperrefort@pitt.edu',
      url='https://github.com/mwvgroup/pwv_kpno',
      license='GPL v3',

      python_requires='>=2.7',
      install_requires=['numpy', 'astropy', 'requests', 'pytz', 'scipy'],
      package_data={'pwv_kpno': DATA_FILES},
      include_package_data=True
      )
