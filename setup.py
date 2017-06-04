from distutils.core import setup


def long_description():
    return 'Long description'
    # with open('README.txt') as ofile:
    #     return ofile.read()

setup(name='pwv_kpno',
      version='1.0.0',
      description='Corrects NIR spectra taken at KPNO using atmospheric models',
      long_description=long_description(),
      classifiers=['Development Status :: 3 - Alpha',
                   'Framework :: Django',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Scientific/Engineering :: Atmospheric Science',
                   'Topic :: Scientific/Engineering :: Physics'],

      keywords=['KPNO', 'atmosphere', 'atmospheric correction'],
      url='noUrl',
      author='Daniel Perrefort',
      author_email='djp81@pitt.edu',
      license='GPL v3',
      packages=['pwv_kpno'],
      install_requires=[
          'numpy',
          'astropy',
          ]
    )
