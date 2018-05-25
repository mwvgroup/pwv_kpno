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
TEMP_0 = 8000


def source_dict(bb_temp, pwv):
    """Create a source for a given PWV column density"""

    transmission_model = pwv_atm.trans_for_pwv(pwv)

    wavelengths = np.array(transmission_model['wavelength'])
    transmission = np.array(transmission_model['transmission'])
    b_body = bb_atm.sed(bb_temp, wavelengths, 0)
    b_body_atm = bb_atm.sed(bb_temp, wavelengths, pwv)

    i_model = transmission_model[wavelengths < 8500]
    i_scale_const = np.trapz(i_model['transmission'], i_model['wavelength'])
    i_scale_const /= (max(i_model['wavelength']) - min(i_model['wavelength']))

    z_model = transmission_model[8500 < wavelengths]
    z_scale_const = np.trapz(z_model['transmission'], z_model['wavelength'])
    z_scale_const /= (max(z_model['wavelength']) - min(z_model['wavelength']))

    data_dict = dict(
        transmission=transmission,
        wavelengths=wavelengths,
        b_body=b_body,
        b_body_atm=b_body_atm,
        b_body_iscale=b_body * i_scale_const,
        b_body_zscale=b_body * z_scale_const
    )

    return data_dict


# Set up plot
source = ColumnDataSource(data=source_dict(8000, PWV_0))
fig_args = dict(plot_width=400, plot_height=400, y_range=(0, 1E7), title=None)

s1 = figure(**fig_args, x_range=(7000, 8500))
s1.line('wavelengths', 'b_body_atm', source=source, color="navy", alpha=.75)
s1.line('wavelengths', 'b_body', source=source, color="green", line_width=1.75)
s1.line('wavelengths', 'b_body_iscale', source=source, color="red", line_width=1.75)
s1.yaxis.axis_label = 'Black Body Flux (ergs / s / A / cm^2 / sr)'
s1.xaxis.axis_label = 'Wavelength'

s2 = figure(**fig_args, x_range=(8500, 10000))
s2.line('wavelengths', 'b_body_atm', source=source, color="navy", alpha=.75, legend='With Atmosphere')
s2.line('wavelengths', 'b_body', source=source, color="green", line_width=1.75, legend='Black Body')
s2.line('wavelengths', 'b_body_zscale', source=source, color="red", line_width=1.75, legend='Scaled by absorption')
s2.xaxis.axis_label = 'Wavelength'
s2.legend.location = "top_right"
s2.legend.click_policy = "hide"

plot = gridplot([[s1, s2]], toolbar_location=None)


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
