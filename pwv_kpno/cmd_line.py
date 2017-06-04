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


# We create wrapper functions that pass command line arguments to functions
# imported from pwv_kpno/end_user_functions.py. For more information on these
# functions documentation is included in pwv_kpno/end_user_functions.py and
# also in README.MD

def available_data_wrapper(cli_args):
    """Print a set of years for which SuomiNet data is locally available

    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    print('Found data for: {0}\n'.format(available_data()))

def update_models_wrapper(cli_args):
    """Update the local SuomiNet data with new data from SuomiNet's website

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
    """Write a copy of the local SuomiNet data to a .csv file

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
    """Write a copy of the PWV model for Kitt Peak to a .csv file

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
    """Write to file the modeled transmission due to PWV for a given datetime

    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    date = datetime(year=cli_args.year, month=cli_args.month,
                    day=cli_args.day, hour=cli_args.hour,
                    minute=cli_args.minute)

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
UPDATE_DESC = 'Update the local SuomiNet data and PWV models.'
UPDATE_YHLP = ('The year to download local data for. If unspecified,' +
               ' data is updated for all available years.')

UPDATE_PRSR = SUBPARSERS.add_parser('update_models', description=UPDATE_DESC)
UPDATE_PRSR.set_defaults(func=update_models_wrapper)
UPDATE_PRSR.add_argument('-y', '--year', type=int, default=None, help=UPDATE_YHLP)

# Create a command line subparser for the measured_pwv_wrapper function
MEASUR_DESC = 'Write a copy of the local SuomiNet data to a .csv file.'
MEASUR_OHLP = 'The desired output file path'
MEASUR_YHLP = 'Include only measurements taken during a specified year'
MEASUR_MHLP = 'Include only measurements taken during a specified month'
MEASUR_DHLP = 'Include only measurements taken during a specified day'
MEASUR_HHLP = 'Include only measurements taken during a specified hour'

MEASUR_PRSR = SUBPARSERS.add_parser('measured_pwv', description=MEASUR_DESC)
MEASUR_PRSR.set_defaults(func=measured_pwv_wrapper)
MEASUR_PRSR.add_argument('-o', '--output', type=str, help=MEASUR_OHLP)
MEASUR_PRSR.add_argument('-y', '--year', type=int, default=None, help=MEASUR_YHLP)
MEASUR_PRSR.add_argument('-m', '--month', type=int, default=None, help=MEASUR_MHLP)
MEASUR_PRSR.add_argument('-d', '--day', type=int, default=None, help=MEASUR_DHLP)
MEASUR_PRSR.add_argument('-H', '--hour', type=int, default=None, help=MEASUR_HHLP)

# Create a command line subparser for the modeled_pwv_wrapper function
MODLED_DESC = 'Write a copy of the PWV model for Kitt Peak to a .csv file.'
MODLED_OHLP = 'The desired output file path'
MODLED_YHLP = 'Restrict the model to a specified year'
MODLED_MHLP = 'Restrict the model to a specified month'
MODLED_DHLP = 'Restrict the model to a specified day'
MODLED_HHLP = 'Restrict the model to a specified hour'

MODLED_PRSR = SUBPARSERS.add_parser('modeled_pwv', description=MODLED_DESC)
MODLED_PRSR.set_defaults(func=modeled_pwv_wrapper)
MODLED_PRSR.add_argument('-o', '--output', type=str, help=MODLED_OHLP)
MODLED_PRSR.add_argument('-y', '--year', type=int, default=None, help=MODLED_YHLP)
MODLED_PRSR.add_argument('-m', '--month', type=int, default=None, help=MODLED_MHLP)
MODLED_PRSR.add_argument('-d', '--day', type=int, default=None, help=MODLED_DHLP)
MODLED_PRSR.add_argument('-H', '--hour', type=int, default=None, help=MODLED_HHLP)

# Create command line subparser for the transmission_wrapper function
TRANSM_DESC = ('Get the modeled atmospheric transmission spectrum for' +
               ' a given date and airmass.')
TRANSM_AHLP = 'The airmass of the desired model spectrum'
TRANSM_OHLP = 'The desired output file path'
TRANSM_YHLP = 'The year of the desired model spectrum'
TRANSM_MHLP = 'The month of the desired model spectrum'
TRANSM_DHLP = 'The day of the desired model spectrum'
TRANSM_HHLP = 'The hour of the desired model spectrum'
TRANSM_MIHLP = 'The minute of the desired model spectrum'

TRANSM_PRSR = SUBPARSERS.add_parser('transmission', description=TRANSM_DESC)
TRANSM_PRSR.set_defaults(func=transmission_wrapper)
TRANSM_PRSR.add_argument('-o', '--output', type=str, help=TRANSM_OHLP)
TRANSM_PRSR.add_argument('-y', '--year', type=int, default=None, help=TRANSM_YHLP)
TRANSM_PRSR.add_argument('-m', '--month', type=int, default=None, help=TRANSM_MHLP)
TRANSM_PRSR.add_argument('-d', '--day', type=int, default=None, help=TRANSM_DHLP)
TRANSM_PRSR.add_argument('-H', '--hour', type=int, default=None, help=MEASUR_HHLP)
TRANSM_PRSR.add_argument('-M', '--minute', type=int, default=None, help=TRANSM_MIHLP)
TRANSM_PRSR.add_argument('-a', '--airmass', type=float, help=TRANSM_AHLP)

if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    ARGS.func(ARGS)

