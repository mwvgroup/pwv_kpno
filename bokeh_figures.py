#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, gridplot
from bokeh.models import Slider
from bokeh.plotting import figure, ColumnDataSource
import numpy as np

from pwv_kpno import pwv_atm
from pwv_kpno import blackbody_with_atm as bb_atm

PWV_0 = 15
TEMP_0 = 8500


def source_dict(bb_temp, pwv):
    """Create a source for a given PWV column density"""

    transmission_model = pwv_atm.trans_for_pwv(pwv)

    wavelengths = np.array(transmission_model['wavelength'])
    transmission = np.array(transmission_model['transmission'])
    b_body = bb_atm.sed(bb_temp, wavelengths, 0)
    b_body_atm = bb_atm.sed(bb_temp, wavelengths, pwv)

    data_dict = dict(
        transmission=transmission,
        wavelengths=wavelengths,
        b_body=b_body,
        b_body_atm=b_body_atm,
    )

    return data_dict


# Set up plot
source = ColumnDataSource(data=source_dict(TEMP_0, PWV_0))
fig_args = dict(plot_width=800, plot_height=400, y_range=(0, 2E7), title=None)

s1 = figure(**fig_args, x_range=(3000, 12000))
s1.line('wavelengths', 'b_body_atm', source=source, color="navy", alpha=.75)
s1.line('wavelengths', 'b_body', source=source, color="green", line_width=1.75)
s1.yaxis.axis_label = 'Black Body Flux (ergs / s / A / cm^2 / sr)'
s1.xaxis.axis_label = 'Wavelength'

plot = gridplot([[s1]], toolbar_location='right')


# Set up widgets
temp_slider = Slider(title="Black Body Temperature (K)", value=TEMP_0, start=7000, end=10000, step=100)
pwv_slider = Slider(title="PWV Column Density (mm)", value=PWV_0, start=0.0, end=30.0, step=0.5)


def update_data(attr, old, new):
    """Update the figure source for a new PWV column density"""

    source.data = source_dict(temp_slider.value, pwv_slider.value)


temp_slider.on_change('value', update_data)
pwv_slider.on_change('value', update_data)

inputs = widgetbox(pwv_slider, temp_slider)
curdoc().add_root(row(plot, inputs, width=800))
curdoc().title = "Atmospheric Effects on Black Bodies"
