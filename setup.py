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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pwv_kpno.  If not, see <http://www.gnu.org/licenses/>.

# Because I know I will be looking for thread later on:
# https://stackoverflow.com/q/7522250

from setuptools import setup


def long_description():
    with open('README.md') as ofile:
        readme = ofile.read()

        # Get the Package Description without headers
        description = readme.split('## 1) Package Description')[-1]
        description = description.replace('\n## 2) Documentation', '')

        # Remove markdown formating
        description = description.replace('*', '')
        description = description.replace('[here]', '')
        description = description.replace('[', '').replace(']', ' ')
        return description


setup(name='pwv_kpno',
      version='0.10.1',
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
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      include_package_data=True)
