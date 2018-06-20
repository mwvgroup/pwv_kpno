# For Developers

The following is provided as a reference for current and future developers.



## 1. Future Features

Some intended features to be included in future development include:

- Include an option or function to return the atmospheric transmission binned at different wavelengths.
- Add the ability to create new atmospheric models for an arbitrary SuomiNet location.
- Implement functions to export / import custom made models and affiliated data so that resources can be shared between collaborators or made public.
- Extend the atmospheric models to include a wider wavelength range.
- An upper limit could be imposed on the number of significant figures returned by each function.

**Note:** The **pwv_kpno** package depends on atmospheric models parsed by create_atm_model.py. These models only consider the effects of precipitable water vapor, but can be modified to include the effects of o2 and o3. The necessary code for this is commented out within the file.



## 2. Updating Package Documentation

### 2.1 Extra Dependencies

Source code for the documentation can be found in the *gh-pages* branch of the [project repository](https://github.com/mwvgroup/pwv_kpno/tree/gh-pages). Documentation for **pwv_kpno** is generated using Sphinx and the “Read The Docs” theme. To update or modify package documentation you will need to install both of these. Note that version 0.2.4 has known bugs that will cause the documentation to not render correctly.

```bash
$ pip install sphinx
$ pip install "sphinx_rtd_theme>0.2.4"    
```



###  2.2 Generating new files

Source code for all documentation is contained in the rst_source directory. Files in other subdirectories are generated automatically and should not be edited. A new version of the documentation can be automatically generated by running the following from the project root directory:

```bash
$ cd rst_source
$ make gh-pages
```

The make file will automatically create new folder named with the current package version and fill it with newly generated documentation. Any documentation that may already exist for that version will be overwritten. To modify the default documentation version that appears on the project website, edit index.html in the root directory.

Note that the usage examples in the documentation, including dates, are hard coded. The make file will not update any demonstrated code outputs to reflect new code changes. The sphinx configuration file rst_source/conf.py is also not setup for any documentation formats supported by sphinx other than html (such as Texinfo, LaTeX, or HTMLHelp).



## 3. Releasing a New Version

New package versions should be released at least every year, and should include all relevant SuomiNet data from 2010 through the previous year. No SuomiNet data should be included for the year that the new version is released. To release a new version, follow the following steps:

1. Make sure that the build passes on <travis-ci.org>.
2. Update the meta data in __init__.py and the badges in README.md to reflect the new version number and any newly supported Python versions.
3. Proofread package docstring for both spelling and accuracy.
4. Generate new documentation using sphinx.
5. Merge the new source code into `master`.
6. Merge any new documentation into `gh-pages`.
7. Run the push_pypi bash file from the root directory to automatically upload the new version to the python package index (you will need the appropriate login information for this step).