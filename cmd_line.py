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
from pytz import utc

from pwv_kpno import __version__ as version
from pwv_kpno._transmission import trans_from_date
from pwv_kpno._transmission import trans_from_pwv
from pwv_kpno._pwv_data import available_data
from pwv_kpno._pwv_data import measured_pwv
from pwv_kpno._pwv_data import modeled_pwv
from pwv_kpno._pwv_data import update_models

__author__ = 'Daniel Perrefort'
__copyright__ = 'Copyright 2017, Daniel Perrefort'

__license__ = 'GPL V3'
__email__ = 'djperrefort@gmail.com'
__status__ = 'Development'


# We create wrapper functions that pass command line arguments to functions
# imported from calc_transmission.py. For more information on these functions
# documentation is included in calc_transmission.py and also in README.MD

def available_data_wrapper(cli_args):
    """Print a set of years for which SuomiNet data is locally available

    args:
        cli_args (argparse.Namespace): Arguments from the command line
    """

    print('Found data for: {0}\n'.format(available_data()))


def update_models_wrapper(cli_args):
    """Update the local SuomiNet data with new data from SuomiNet's website

    args:
        cli_args (argparse.Namespace): Arguments from the command line
    """

    years = update_models(cli_args.year)
    if years:
        print('Data and models have been updated for {0}\n'.format(years))

    else:
        print('No SuomiNet data found.\n')


def measured_pwv_wrapper(cli_args):
    """Write a copy of the local SuomiNet data to a comma delimited file

    args:
        cli_args (argparse.Namespace): Arguments from the command line
    """

    data = measured_pwv(year=cli_args.year, month=cli_args.month,
                        day=cli_args.day, hour=cli_args.hour)

    data.write(cli_args.output, overwrite=cli_args.force, format='ascii.csv')


def modeled_pwv_wrapper(cli_args):
    """Write a copy of the PWV model for Kitt Peak to a comma delimited file

    args:
        cli_args (argparse.Namespace): Arguments from the command line
    """

    data = modeled_pwv(year=cli_args.year, month=cli_args.month,
                       day=cli_args.day, hour=cli_args.hour)

    data.write(cli_args.output, overwrite=cli_args.force, format='ascii.csv')


def transmission_pwv_wrapper(cli_args):
    """Write to file the modeled transmission due to PWV for a given datetime

    args:
        cli_args (argparse.Namespace): Arguments from the command line
    """

    model = trans_from_pwv(cli_args.pwv)
    model.write(cli_args.output, overwrite=cli_args.force, format='ascii.csv')


def transmission_wrapper(cli_args):
    """Write to file the modeled transmission due to PWV for a given datetime

    args:
        cli_args (argparse.Namespace): Arguments from the command line
    """

    date = datetime(year=cli_args.year,
                    month=cli_args.month,
                    day=cli_args.day,
                    hour=cli_args.hour,
                    minute=cli_args.minute,
                    tzinfo=utc)

    model = trans_from_date(date, cli_args.airmass)
    model.write(cli_args.output, overwrite=cli_args.force, format='ascii.csv')


# Create an argument parser to handle command line arguments
PARSER = argparse.ArgumentParser()
PARSER.add_argument('-v', '--version', action='version', version=version)
SUBPARSERS = PARSER.add_subparsers()

# Create a command line sub-parser for the available_data_wrapper function
DA_DESC = "Return a set of years for which local SuomiNet data is available."

DA_PRSR = SUBPARSERS.add_parser('available_data', description=DA_DESC)
DA_PRSR.set_defaults(func=available_data_wrapper)

# Create a command line sub-parser for the update_models_wrapper
UP_DESC = 'Update the local SuomiNet data and PWV models.'
UP_YHLP = ('The year to download local data for. If unspecified,' +
           ' data is updated for all available years.')

UP_PRSR = SUBPARSERS.add_parser('update_models', description=UP_DESC)
UP_PRSR.set_defaults(func=update_models_wrapper)
UP_PRSR.add_argument('-y', '--year', type=int, default=None, help=UP_YHLP)

# Create a command line sub-parser for the measured_pwv_wrapper function
ME_DESC = 'Write a copy of the local SuomiNet data to a .csv file.'
ME_OHLP = 'The desired output file path'
ME_FHLP = 'Whether to overwrite an existing file (default false)'
ME_YHLP = 'Only include measurements for a specified year'
ME_MHLP = 'Only include measurements for a specified month'
ME_DHLP = 'Only include measurements for a specified day'
ME_HHLP = 'Only include measurements for a specified hour'

ME_PRSR = SUBPARSERS.add_parser('measured_pwv', description=ME_DESC)
ME_PRSR.set_defaults(func=measured_pwv_wrapper)
ME_PRSR.add_argument('-o', '--output', type=str, required=True, help=ME_OHLP)
ME_PRSR.add_argument('-f', '--force', type=bool, default=False, help=ME_FHLP)
ME_PRSR.add_argument('-y', '--year', type=int, default=None, help=ME_YHLP)
ME_PRSR.add_argument('-m', '--month', type=int, default=None, help=ME_MHLP)
ME_PRSR.add_argument('-d', '--day', type=int, default=None, help=ME_DHLP)
ME_PRSR.add_argument('-H', '--hour', type=int, default=None, help=ME_HHLP)

# Create a command line sub-parser for the modeled_pwv_wrapper function
MO_DESC = 'Write a copy of the PWV model for Kitt Peak to a .csv file.'
MO_OHLP = 'The desired output file path'
MO_FHLP = 'Whether to overwrite an existing file (default false)'
MO_YHLP = 'Only include model values for a specified year'
MO_MHLP = 'Only include model values for a specified month'
MO_DHLP = 'Only include model values for a specified day'
MO_HHLP = 'Only include model values for a specified hour'

MO_PRSR = SUBPARSERS.add_parser('modeled_pwv', description=MO_DESC)
MO_PRSR.set_defaults(func=modeled_pwv_wrapper)
MO_PRSR.add_argument('-o', '--output', type=str, required=True, help=MO_OHLP)
MO_PRSR.add_argument('-f', '--force', type=bool, default=False, help=MO_FHLP)
MO_PRSR.add_argument('-y', '--year', type=int, default=None, help=MO_YHLP)
MO_PRSR.add_argument('-m', '--month', type=int, default=None, help=MO_MHLP)
MO_PRSR.add_argument('-d', '--day', type=int, default=None, help=MO_DHLP)
MO_PRSR.add_argument('-H', '--hour', type=int, default=None, help=MO_HHLP)

# Create command line sub-parser for the transmission_wrapper function
TRD_DESC = ('Get the modeled atmospheric transmission spectrum for' +
            ' a given date and airmass.')
TRD_OHLP = 'The desired output file path'
TRD_FHLP = 'Whether to overwrite an existing file (default false)'
TRD_AHLP = 'The airmass of the desired model spectrum'
TRD_YHLP = 'The year of the desired model spectrum'
TRD_MHLP = 'The month of the desired model spectrum'
TRD_DHLP = 'The day of the desired model spectrum'
TRD_HHLP = 'The hour of the desired model spectrum (default 0)'
TRD_MIHLP = 'The minute of the desired model spectrum (default 0)'

TRD_PRSR = SUBPARSERS.add_parser('transmission', description=TRD_DESC)
TRD_PRSR.set_defaults(func=transmission_wrapper)
TRD_PRSR.add_argument('-o', '--output', type=str, required=True, help=TRD_OHLP)
TRD_PRSR.add_argument('-f', '--force', type=bool, default=False, help=TRD_FHLP)
TRD_PRSR.add_argument('-a', '--airmass', type=float,
                      required=True, help=TRD_AHLP)
TRD_PRSR.add_argument('-y', '--year', type=int, required=True, help=TRD_YHLP)
TRD_PRSR.add_argument('-m', '--month', type=int, required=True, help=TRD_MHLP)
TRD_PRSR.add_argument('-d', '--day', type=int, required=True, help=TRD_DHLP)
TRD_PRSR.add_argument('-H', '--hour', type=int, default=0, help=TRD_HHLP)
TRD_PRSR.add_argument('-M', '--minute', type=int, default=0, help=TRD_MIHLP)

# Create command line sub-parser for the transmission_pwv_wrapper function
TRP_DESC = ('Get the modeled atmospheric transmission spectrum for' +
            ' a known PWV concentration along line of sight in mm.')
TRP_OHLP = 'The desired output file path'
TRP_FHLP = 'Whether to overwrite an existing file (default false)'
TRP_PHLP = 'The PWV concentration along line of sight in mm'

TRP_PRSR = SUBPARSERS.add_parser('transmission_pwv', description=TRP_DESC)
TRP_PRSR.set_defaults(func=transmission_pwv_wrapper)
TRP_PRSR.add_argument('-o', '--output', type=str, required=True, help=TRP_OHLP)
TRP_PRSR.add_argument('-f', '--force', type=bool, default=False, help=TRP_FHLP)
TRP_PRSR.add_argument('-p', '--pwv', type=float, required=True, help=TRP_PHLP)

if __name__ == '__main__':
    ARGS = PARSER.parse_args()
    ARGS.func(ARGS)
