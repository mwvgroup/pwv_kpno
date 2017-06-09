## Future work:

- Return transmission binned for certain wavelengths
- When working with SED's, if I calibrated with a star of a certain color, what error did I make in z that didn't account for pwv absorption

## Notes for developers:

- atm models can also model additional info - necessary code is commented out
- wavelength range in interpolate function needs to be changed if you change the range of the models
- Make sure config.txt and local data are present - there are no checks
- before dist: reset config file, overwrite suomi data, and change DIST_YEAR variable in create_pwv_models.py
- when releasing new version change STRT_YEAR in create_pwv_models.py
- also update the update_models description to indicate what years are included by default 