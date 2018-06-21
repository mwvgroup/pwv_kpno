import numpy as np
from bokeh.layouts import row, widgetbox, gridplot
from bokeh.models import CustomJS, Slider
from bokeh.plotting import figure, output_file, show, ColumnDataSource

import pwv_kpno as pk


def create_source():
    """Create a table with the transmission for different PWV values

    Returns:

    """

    pwv_model = pk.pwv_atm.trans_for_pwv(0)
    wavelengths = np.array(pwv_model['wavelength'])
    b_body = pk.blackbody_with_atm.sed(8000, wavelengths, 0)
    data = {'wavelength': wavelengths,
            't_00.0': pwv_model['transmission'],
            'b_00.0': b_body}

    for pwv in np.arange(1, 30, 1):
        pwv_model = pk.pwv_atm.trans_for_pwv(pwv)
        b_body = pk.blackbody_with_atm.sed(8000, wavelengths, pwv)

        key = '{:.1f}'.format(pwv).zfill(4)
        data['t_' + key] = pwv_model['transmission']
        data['b_' + key] = b_body

    data['transmission'] = data['t_15.0']
    data['black_body'] = data['b_15.0']
    return ColumnDataSource(data=data)


def create_figure(out_path):
    source = create_source()
    trans_plot = figure(plot_width=800, plot_height=200, y_range=(0, 1))
    trans_plot.line('wavelength', 'transmission', source=source, line_width=1)

    bb_plot = figure(plot_width=800, plot_height=500, y_range=(0, 1.5E7))
    bb_plot.line('wavelength', 'black_body', source=source, line_width=1)
    bb_plot.line('wavelength', 'b_00.0', source=source, line_width=1)

    callback = CustomJS(args=dict(source=source), code="""
        var data = source.data;
        var key = ("00" + pwv.value.toFixed(1)).slice(-4);
        data['transmission'] = data["t_" + key];
        data['black_body'] = data["b_" + key];
        source.change.emit();
    """)

    pwv_slider = Slider(start=0, end=30, value=15, step=1, title="PWV",
                        callback=callback)
    callback.args["pwv"] = pwv_slider

    plot = gridplot([[trans_plot], [bb_plot], [pwv_slider]],
                    toolbar_location='left')
    output_file(out_path, title="slider.py example")
    show(plot)


if __name__ == '__main__':
    create_figure('slider.html')
