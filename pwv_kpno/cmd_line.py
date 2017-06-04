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

"""This code provides a command line interface for the pwv_kpno package."""

import argparse
from datetime import datetime

from __init__ import __version__ as VERSION
from end_user_functions import available_data
from end_user_functions import update_models
from end_user_functions import measured_pwv
from end_user_functions import modeled_pwv
from end_user_functions import transmission

__author__ = 'Daniel Perrefort'
__email__ = 'djperrefort@gmail.com'
__copyright__ = 'Copyright 2017, Daniel Perrefort'
__license__ = 'GPL V3'
__status__ = 'Development'


def available_data_wrapper(cli_args):
    """A wrapper function that passes command line arguments to available_data

    The available_data function returns a set of years for which SuomiNet data
    For more information on the available_data function see end_user_functions.py.
    
    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    print('Found data for: {0}\n'.format(available_data()))

def update_models_wrapper(cli_args):
    """A wrapper function that passes command line arguments to update_models

    The update_models function updates the locally stored SUomiNet data by
    downloading new data from SuomiNet's website. For more information on the
    update_models function see end_user_functions.py.

    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    years = update_models(cli_args.year)
    if years:
        print('Data and models have been updated for {0}\n'.format(*years))
    
    else:
        print('No SuomiNet data found.\n')


def measured_pwv_wrapper(cli_args):
    """A wrapper function that passes command line arguments to measured_pwv

    The measured_pwv function returns an astropy table of PWV measurements
    taken by SuomiNet. For more information on the nearest_value function,
    see get_pwv_data.py.

    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    data = measured_pwv(year=cli_args.year, month=cli_args.month,
                        day=cli_args.day, hour=cli_args.hour)

    if cli_args.output.endswith('.csv'):
        data.write(cli_args.output, overwrite=False)
    
    else:
        data.write(cli_args.output + '.csv', overwrite=False)


def modeled_pwv_wrapper(cli_args):
    """A wrapper function that passes command line arguments to modeled_pwv

    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    data = modeled_pwv(year=cli_args.year, month=cli_args.month,
                       day=cli_args.day, hour=cli_args.hour)

    if cli_args.output.endswith('.csv'):
        data.write(cli_args.output, overwrite=False)
    
    else:
        data.write(cli_args.output + '.csv', overwrite=False)


def transmission_wrapper(cli_args):
    """A wrapper function that passes command line arguments to transmission

    Format command line arguments and pass them to the date_to_spectra
    function, which returns the modeled atmospheric transmission spectrum for a
    given date date and airmass. For more information on date_to_spectra, see
    datetime_to_spectra.py.

    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    date = datetime(year=cli_args.year, month=cli_args.month,
                    day=cli_args.day, hour=cli_args.hour)

    transmission = date_to_spectra(date, cli_args.airmass)
    if cli_args.output.endswith('.csv'):
        transmission.write(cli_args.output, overwrite=False)
    
    else:
        transmission.write(cli_args.output + '.csv', overwrite=False)


# Create an argument parser to handle command line arguments
PARSER = argparse.ArgumentParser()
PARSER.add_argument('-v', '--version', action='version', version=VERSION)
SUBPARSERS = PARSER.add_subparsers()

# Create a command line subparser for the available_data_wrapper function
AVDATA_DESC = "Return a set of years for which SuomiNet data is locally available."

AVDATA_PRSR = SUBPARSERS.add_parser('available_data', description=AVDATA_DESC)
AVDATA_PRSR.set_defaults(func=available_data_wrapper)

# Create a command line subparser for the update_models_wrapper
UPDATE_DESC = 'Update the local SuomiNet data and atmospheric models.'
UPDATE_YHLP = ('The year to update local data for. If unspecified,' +
               ' data is updated for all available years.')

UPDATE_PRSR = SUBPARSERS.add_parser('update_models', description=UPDATE_DESC)
UPDATE_PRSR.set_defaults(func=update_models_wrapper)
UPDATE_PRSR.add_argument('-y', '--year', type=int, default=None, help=UPDATE_YHLP)

# Create a command line subparser for the measured_pwv_wrapper function
MEASUR_DESC = 'Write a copy of the local SuomiNet data to a .csv file.'
MEASUR_OHLP = 'The desired output file path,'
MEASUR_YHLP = 'Include only measurments taken durring a specified year.'
MEASUR_MHLP = 'Include only measurments taken durring a specified month.'
MEASUR_DHLP = 'Include only measurments taken durring a specified day.'
MEASUR_THLP = 'Include only measurments taken durring a specified hour.'

MEASUR_PRSR = SUBPARSERS.add_parser('measured_pwv', description=MEASUR_DESC)
MEASUR_PRSR.set_defaults(func=measured_pwv_wrapper)
MEASUR_PRSR.add_argument('-o', '--output', type=str, help=MEASUR_OHLP)
MEASUR_PRSR.add_argument('-y', '--year', type=int, default=None, help=MEASUR_YHLP)
MEASUR_PRSR.add_argument('-m', '--month', type=int, default=None, help=MEASUR_MHLP)
MEASUR_PRSR.add_argument('-d', '--day', type=int, default=None, help=MEASUR_DHLP)
MEASUR_PRSR.add_argument('-t', '--hour', type=int, default=None, help=MEASUR_THLP)

# Create a command line subparser for the modeled_pwv_wrapper function
MEASUR_PRSR = SUBPARSERS.add_parser('modeled_pwv', description=MEASUR_DESC)
MEASUR_PRSR.set_defaults(func=modeled_pwv_wrapper)
MEASUR_PRSR.add_argument('-o', '--output', type=str, help=MEASUR_OHLP)
MEASUR_PRSR.add_argument('-y', '--year', type=int, default=None, help=MEASUR_YHLP)
MEASUR_PRSR.add_argument('-m', '--month', type=int, default=None, help=MEASUR_MHLP)
MEASUR_PRSR.add_argument('-d', '--day', type=int, default=None, help=MEASUR_DHLP)
MEASUR_PRSR.add_argument('-t', '--hour', type=int, default=None, help=MEASUR_THLP)

# Create command line subparser for the transmission_wrapper function
TRANSM_DESC = ('Get the modeled atmospheric transmission spectrum for' +
               ' a given date and airmass.')
TRANSM_AHLP = 'The airmass for the desired model spectrum.'

TRANSM_PRSR = SUBPARSERS.add_parser('atm_spectra', description=ATMSPC_DESC)
TRANSM_PRSR.set_defaults(func=date_to_spectra_wrapper)
TRANSM_PRSR.add_argument('-o', '--output', type=str, help=MEASUR_OHLP)
TRANSM_PRSR.add_argument('-y', '--year', type=int, default=None, help=MEASUR_YHLP)
TRANSM_PRSR.add_argument('-m', '--month', type=int, default=None, help=MEASUR_MHLP)
TRANSM_PRSR.add_argument('-d', '--day', type=int, default=None, help=MEASUR_DHLP)
TRANSM_PRSR.add_argument('-t', '--hour', type=int, default=None, help=MEASUR_THLP)
TRANSM_PRSR.add_argument('-a', '--airmass', type=float, help=TRANSM_AHLP)

if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    ARGS.func(ARGS)

