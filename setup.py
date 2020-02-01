#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the pwv_kpno software package.
#
#    The pwv_kpno package is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The pwv_kpno package is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#    Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pwv_kpno.  If not, see <http://www.gnu.org/licenses/>.

# Because I know I will be looking for this thread later on:
# https://stackoverflow.com/q/7522250

import re
from pathlib import Path

from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


def long_description():
    with open('README.md') as ofile:
        readme = ofile.readlines()

    description = ' '.join(readme[13:])
    return description


# Get package version
init_path = Path(__file__).resolve().parent / 'pwv_kpno/__init__.py'
with open(init_path, 'r') as f:
    s = f.read()

versionRegExp = re.compile("__version__ = '(.*?)'")
__version__ = versionRegExp.findall(s)[0]

setup(name='pwv_kpno',
      version=__version__,
      packages=['pwv_kpno'],
      keywords='KPNO atmospheric transmission PWV precipitable water vapor',
      description='Models the atmospheric transmission function for KPNO',
      long_description=long_description(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Astronomy',
          'Topic :: Scientific/Engineering :: Atmospheric Science',
          'Topic :: Scientific/Engineering :: Physics'
      ],

      author='Daniel Perrefort',
      author_email='djperrefort@pitt.edu',
      url='https://mwvgroup.github.io/pwv_kpno/',
      license='GPL v3',

      python_requires='>=3.6',
      install_requires=requirements,

      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      include_package_data=True)
