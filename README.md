# pwv_kpno module

#### Developer notes:
- atm models can also model additional info - necessary code is commented out
- wavelength range in interpolate function needs to be changed if you change the range of the models
- user needs permission to update files within the package when updating pwv data
- dev notes - Make sure config.txt and local data are present - there are no checks
- before dist: reset config file, overwrite suomi data, and change DIST_YEAR variable in create_pwv_models.py
