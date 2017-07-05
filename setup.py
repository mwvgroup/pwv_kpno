#!/usr/bin/env python3
try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

setup(name='pwv_kpno',
	  version='0.9.7',
	  description='Models the atmospheric transmission function for KPNO',
	  long_description=open('README.md').read()[917:],
	  classifiers=['Development Status :: 4 - Beta',
				   'Intended Audience :: Science/Research',
				   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
				   'Natural Language :: English',
				   'Operating System :: OS Independent',
				   'Programming Language :: Python',
				   'Programming Language :: Python :: 2.7',
				   'Programming Language :: Python :: 3.69',
				   'Topic :: Scientific/Engineering :: Astronomy',
				   'Topic :: Scientific/Engineering :: Atmospheric Science',
				   'Topic :: Scientific/Engineering :: Physics'],

	  keywords='KPNO atmospheric transmission PWV precipitable water vapor',
	  url='https://github.com/mwvgroup/pwv_kpno',
	  author='Daniel Perrefort',
	  author_email='djp81@pitt.edu',
	  license='GPL v3',
	  packages=['pwv_kpno'],
	  python_requires='>=2.7',
	  install_requires=['numpy', 'astropy', 'scipy', 'requests', 'pytz'],
	  )
