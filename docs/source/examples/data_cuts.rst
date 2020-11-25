*********************
Visualizing Data Cuts
*********************

For various reasons, you may wish to apply cuts to the SuomiNet measurements
used by **pwv_kpno**. The most obvious use case would be to ignore a period of
time when a SuomiNet weather station was experiencing technical difficulties,
or if there is some unexplained, unphysical spike in the measurements. For
convenience, we demonstrate how to visually explore various choices in data cuts.

Applying Data Cuts
------------------

Following the SuomiNet naming convention, data cuts can be defined for
the values listed below. Note that most data cuts are inclusive and define what data
to **keep**. However, cuts on date values are exclusive and define what
values to **ignore**.

+--------------+------------------+--------------------+
| Value Name   | Units            | Cut Type           |
+==============+==================+====================+
| Date         | UTC Timestamp    | Exclusive          |
+--------------+------------------+--------------------+
| PWV          | Millimeters      | Inclusive          |
+--------------+------------------+--------------------+
| PWVErr       | Millimeters      | Inclusive          |
+--------------+------------------+--------------------+
| ZenithDelay  |                  | Inclusive          |
+--------------+------------------+--------------------+
| SrfcPress    | Millibars        | Inclusive          |
+--------------+------------------+--------------------+
| SrfcTemp     |                  | Inclusive          |
+--------------+------------------+--------------------+
| SrfcRH       | Percentage       | Inclusive          |
+--------------+------------------+--------------------+

Data cuts are associated with ``GPSReceiver`` objects and can be defined
at instantiation:

.. doctest:: python

    >>> from pwv_kpno.gps_pwv import GPSReceiver
    >>>
    >>> azam = GPSReceiver('AZAM', data_cuts={'SrfcPress': [(880, 925), ]})

Data cuts can also be modified for existing instances:

.. doctest:: python

    >>> azam.data_cuts = {'SrfcPress': [(880, 900), ]}
    >>> print(azam.data_cuts)
    {'SrfcPress': [(880, 900), ]}

Visualizing Data Cuts
---------------------
        
We can visually inspect these cuts by using the ``get_all_receiver_data`` to retrieve the
the data with and without the cuts applied and then plotting them as follows:

.. doctest:: python

    >>> from astropy.table import setdiff
    >>> from matplotlib import pyplot as plt
    >>> from pwv_kpno import pwv_atm
    >>> 
    >>> 
    >>> def plot_data_cuts(receiver_id):
    >>>     """Plots PWV vs Temperature, Pressure, and RH at a given SuomiNet site
    >>> 
    >>>     Args:
    >>>         receiver_id (str): A SuomiNet receiver id code (eg. KITT)
    >>>     """
    >>> 
    >>>     # Clear any pre-existing plot data
    >>>     plt.clf()
    >>>     fig = plt.figure(figsize=(8.5, 2))
    >>> 
    >>>     # Get SuomiNet data with and without data cuts
    >>>     all_data = pwv_atm.get_all_receiver_data(receiver_id, apply_cuts=False)
    >>>     data_with_cuts = pwv_atm.get_all_receiver_data(receiver_id, apply_cuts=True)
    >>>     cut_data = setdiff(all_data, data_with_cuts, keys=['date'])
    >>> 
    >>>     # Temperature data
    >>>     axis_label = 'PWV for {}'.format(receiver_id)
    >>>     temp_axis = fig.add_subplot(1, 3, 1)
    >>>     temp_axis.scatter(data_with_cuts['SrfcTemp'], data_with_cuts['PWV'], s=1)
    >>>     temp_axis.scatter(cut_data['SrfcTemp'], cut_data['PWV'], s=1)
    >>>     temp_axis.set_xlabel('SrfcTemp', labelpad=10)
    >>>     temp_axis.set_ylabel(axis_label, labelpad=10)
    >>>     temp_axis.set_xlim(-30, 50)
    >>>     temp_axis.set_ylim(0, 80)
    >>> 
    >>>     # Pressure data
    >>>     press_axis = fig.add_subplot(1, 3, 2)
    >>>     press_axis.scatter(data_with_cuts['SrfcPress'], data_with_cuts['PWV'], s=1)
    >>>     press_axis.scatter(cut_data['SrfcPress'], cut_data['PWV'], s=1)
    >>>     press_axis.set_xlabel('SrfcPress', labelpad=10)
    >>>     press_axis.yaxis.set_ticklabels([])
    >>>     press_axis.set_xlim(650, 850)
    >>>     press_axis.set_ylim(0, 80)
    >>> 
    >>>     # Relative humidity data
    >>>     rh_axis = fig.add_subplot(1, 3, 3)
    >>>     rh_axis.scatter(data_with_cuts['SrfcRH'], data_with_cuts['PWV'], s=1)
    >>>     rh_axis.scatter(cut_data['SrfcRH'], cut_data['PWV'], s=1)
    >>>     rh_axis.set_xlabel('RH', labelpad=10)
    >>>     rh_axis.yaxis.set_ticklabels([])
    >>>     rh_axis.set_xlim(0, 100)
    >>>     rh_axis.set_ylim(0, 80)
    >>> 
    >>>     plt.show()
    >>> 
    >>> plot_data_cuts('KITT')
