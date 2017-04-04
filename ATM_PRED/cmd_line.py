#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

#    This file is part of the atm_pred module.
#
#    The atm_pred module is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The atm_pred module is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with atm_pred.  If not, see <http://www.gnu.org/licenses/>.

"""This code provides a command line interface for the atm_pred package."""

import argparse
from datetime import datetime

from create_pwv_model import update_models
from datetime_to_spectra import nearest_value
from datetime_to_spectra import date_to_spectra

from __init__ import __version__ as VERSION

__author__ = 'Daniel Perrefort'
__email__ = 'djperrefort@gmail.com'
__copyright__ = 'Copyright 2017, Daniel Perrefort'
__license__ = 'GPL V3'
__status__ = 'Development'


def update_models_wrapper(cli_args):
    """A wrapper function that passes command line arguments to update_models

    Format command line arguments and pass them to the update_models function,
    which updates the locally stored PWV data by downloading new data from
    SuomiNet's website. For more info on update_models, see get_pwv_data.py.

    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    if cli_args.year is None:
        years = update_models(cli_args.year, verbose=True)

    else:
        years = update_models(int(cli_args.year), verbose=True)

    print('Updated data for following years:', years, '\n')


def nearest_value_wrapper(cli_args):
    """A wrapper function that passes command line arguments to nearest_value

    Format command line arguments and pass them to the nearest_value function,
    which returns the nearest measured percipitable water vapor measurment
    to a given date. For more info on nearest_value, see get_pwv_data.py.

    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    date = datetime.strptime(cli_args.date, cli_args.format)
    data = nearest_value(date, cli_args.output)
    print('\n', data, '\n')


def date_to_spectra_wrapper(cli_args):
    """A wrapper function that passes command line arguments to date_to_spectra

    Format command line arguments and pass them to the date_to_spectra
    function, which returns the modeled atmospheric transmission spectrum for a
    given date date and airmass. For more information on date_to_spectra, see
    datetime_to_spectra.py.

    args:
        cli_args (argparse.Namespace): Arguments from the command line

    Returns:
        None
    """

    date = datetime.strptime(cli_args.date, cli_args.format)
    date_to_spectra(date, cli_args.airmass, cli_args.output)


# Create an argument parser to handle command line arguments
PARSER = argparse.ArgumentParser()
PARSER.add_argument('-v', '--version', action='version', version=VERSION)
SUBPARSERS = PARSER.add_subparsers()

# Create command line subparser for update_models
UPDATE_DESC = 'Update the local SuomiNet data and atmospheric models.'
UPDATE_YHLP = ('The year to update local data for. If unspecified,' +
               ' data is updated for all available years')

UPDATE_PRSR = SUBPARSERS.add_parser('update_models', description=UPDATE_DESC)
UPDATE_PRSR.set_defaults(func=update_models_wrapper)
UPDATE_PRSR.add_argument('-y', '--year', type=int, default=None,
                         help=UPDATE_YHLP)

# Create command line subparser for nearest_pwv_value
NEAREST_DESC = ('Get the closest measured perciptible water vapor value ' +
                ' to a given datetime')
NEAREST_DHLP = 'The date to search for.'
NEAREST_FHLP = 'The format of the given date. Default is "%Y-%m-%dT%H:%M"'
NEAREST_OHLP = 'If specified, write results to a fits file at this path.'

NEAREST_PRSR = SUBPARSERS.add_parser('pwv_val', description=NEAREST_DESC)
NEAREST_PRSR.set_defaults(func=nearest_value_wrapper)
NEAREST_PRSR.add_argument('-d', '--date', type=str, help=NEAREST_DHLP)
NEAREST_PRSR.add_argument('-f', '--format', type=str, default='%Y-%m-%dT%H:%M',
                          help=NEAREST_FHLP)
NEAREST_PRSR.add_argument('-o', '--output', type=str, default=None,
                          help=NEAREST_OHLP)

# Create command line subparser for atm_spectra
ATMSPC_DESC = ('Get the modeled atmospheric transmission spectrum for' +
               ' a given date and airmass.')
ATMSPC_DHLP = 'The date to search for.'
ATMSPC_FHLP = 'The format of the given date. Default is "%Y-%m-%dT%H:%M"'
ATMSPC_AHLP = 'The airmass for the desired model spectrum. Default is 1.'
ATMSPC_OHLP = 'If specified, write results to a fits file at this path.'

SPECTRA_PRSR = SUBPARSERS.add_parser('atm_spectra', description=ATMSPC_DESC)
SPECTRA_PRSR.set_defaults(func=date_to_spectra_wrapper)
SPECTRA_PRSR.add_argument('-d', '--date', type=str, help=ATMSPC_DHLP)
SPECTRA_PRSR.add_argument('-f', '--format', type=str,
                          default='%Y-%m-%dT%H:%M', help=ATMSPC_FHLP)
SPECTRA_PRSR.add_argument('-a', '--airmass', type=float, default=1,
                          help=ATMSPC_AHLP)
SPECTRA_PRSR.add_argument('-o', '--output', type=str, default=None,
                          help=ATMSPC_OHLP)

if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    ARGS.func(args)
