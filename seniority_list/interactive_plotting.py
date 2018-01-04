#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
.. module:: bokeh_plotting

   :synopsis: The bokeh module contains plotting functions utilizing the
   bokeh plotting library.

.. moduleauthor:: Bob Davison <rubydatasystems@fastmail.net>

'''

from bokeh.plotting import figure, ColumnDataSource
# from bokeh.models import (HoverTool, BoxZoomTool, WheelZoomTool, ResetTool,
#                           PanTool, SaveTool, UndoTool, RedoTool)
from bokeh.models import NumeralTickFormatter, Range1d
from bokeh.models.widgets import Slider, Button, Select
from bokeh.layouts import column, row, widgetbox

import numpy as np
import pandas as pd

'''
TODO:
add stacked area for cat_order
test source.date update using groupby groups/precalculated ColumnDataSources
add size, alpha sliders
make tabs for right side controls
background color selection, alpha control
add datatable
add save underlying data (reports?)
add mark selected employees
add dataset selection
add diff comparison
add hover (with user selection)
add tools (crosshair, etc)
add dataset selection
add dataset group compare
add dataset employee compare
add ret_only
add other chart types
make this the only display??
add persist df
'''


def bk_basic_interactive(doc, df=None,
                         plot_height=700, plot_width=900):
    '''run a basic interactive chart as a server app - powered by the bokeh
    plotting library.  Run the app in the jupyter notebook as follows:

    .. code:: python

        from functools import partial
        import pandas as pd

        import interactive_plotting as ip

        from bokeh.io import show, output_notebook

        from bokeh.application.handlers import FunctionHandler
        from bokeh.application import Application

        output_notebook()

        proposal = 'p1'
        df = pd.read_pickle('dill/ds_' + proposal + '.pkl')

        handler = FunctionHandler(partial(ip.bk_basic_interactive, df=df))

        app = Application(handler)
        show(app)

    inputs
        doc (required, do not change)

        df (dataframe)
            calculated dataset input, this is a required input

        plot_height (integer)
            height of plot in pixels

        plot_width (integer)
            width of plot in pixels

    Add plot_height and/or plot_width parameters as kwargs within the partial
    method:

    .. code:: python

        handler = FunctionHandler(partial(ip.bk_basic_interactive,
                                          df=df,
                                          plot_height=450,
                                          plot_width=625))

    Note: the "df" argument is not optional, a valid dataset variable must
    be assigned.
    '''

    max_month = df['mnum'].max()
    # set up color column
    egs = df['eg'].values
    cdict = pd.read_pickle('dill/dict_color.pkl')
    eg_cdict = cdict['eg_color_dict']
    clr = np.empty(len(df), dtype='object')
    for eg in eg_cdict.keys():
        np.put(clr, np.where(egs == eg)[0], eg_cdict[eg])
    df['c'] = clr
    df['a'] = .7
    df['s'] = 5

    # create empty data source template
    source = ColumnDataSource(data=dict(x=[], y=[], c=[], s=[], a=[]))

    slider_month = Slider(start=0, end=max_month,
                          value=0, step=1,
                          title='month',
                          height=int(plot_height * .6),
                          tooltips=False,
                          bar_color='#ffe6cc',
                          direction='rtl',
                          orientation='vertical',)

    display_attrs = ['age', 'jobp', 'cat_order', 'spcnt', 'lspcnt',
                     'jnum', 'mpay', 'cpay', 'snum', 'lnum',
                     'ylong', 'mlong', 'idx', 'retdate', 'ldate',
                     'doh', 's_lmonths', 'new_order']

    sel_x = Select(options=display_attrs,
                   value='age',
                   title='x axis attribute:',
                   width=115, height=45)
    sel_y = Select(options=display_attrs,
                   value='spcnt',
                   title='y axis attribute:',
                   width=115, height=45)

    but_1add = Button(label='FWD', width=60)
    but_1sub = Button(label='BACK', width=60)
    add_sub = widgetbox(but_1add, but_1sub)

    # x_range = Range1d(df[sel_x].min(), df[sel_x].max())

    def make_plot():
        this_df = get_df()
        xcol = sel_x.value
        ycol = sel_y.value
        source.data = dict(x=this_df[sel_x.value],
                           y=this_df[sel_y.value],
                           c=this_df['c'],
                           a=this_df['a'],
                           s=this_df['s'])

        non_invert = ['age', 'idx', 's_lmonths', 'mlong',
                      'ylong', 'cpay', 'mpay']
        if xcol in non_invert:
            xrng = Range1d(df[xcol].min(), df[xcol].max())
        else:
            xrng = Range1d(df[xcol].max(), df[xcol].min())

        if ycol in non_invert:
            yrng = Range1d(df[ycol].min(), df[ycol].max())
        else:
            yrng = Range1d(df[ycol].max(), df[ycol].min())

        p = figure(plot_width=plot_width,
                   plot_height=plot_height,
                   x_range=xrng,
                   y_range=yrng,
                   # output_backend="webgl",
                   title='')

        p.circle(x='x', y='y', color='c', size='s', alpha='a',
                 line_color=None, source=source)

        pcnt_cols = ['spcnt', 'lspcnt']
        if xcol in pcnt_cols:
            p.x_range.end = -.001
            p.xaxis[0].formatter = NumeralTickFormatter(format="0.0%")
        if ycol in pcnt_cols:
            p.y_range.end = -.001
            p.yaxis[0].formatter = NumeralTickFormatter(format="0.0%")

        if xcol in ['cat_order']:
            p.x_range.end = -50
        if ycol in ['cat_order']:
            p.y_range.end = -50

        if xcol in ['jobp', 'jnum']:
            p.x_range.end = .95
        if ycol in ['jobp', 'jnum']:
            p.y_range.end = .95

        p.xaxis.axis_label = sel_x.value
        p.yaxis.axis_label = sel_y.value

        return p

    def get_df():
        filter_df = df[df.mnum == slider_month.value][[sel_x.value,
                                                       sel_y.value,
                                                       'c', 's', 'a']]

        return filter_df

    def update_data(attr, old, new):
        this_df = get_df()
        # p.title.text = str(slider_month.value)

        source.data = dict(x=this_df[sel_x.value],
                           y=this_df[sel_y.value],
                           c=this_df['c'],
                           a=this_df['a'],
                           s=this_df['s'])

    controls = [sel_x, sel_y]
    wb_controls = [sel_x, sel_y, slider_month]

    for control in controls:
        control.on_change('value', lambda attr, old, new: insert_plot())

    slider_month.on_change('value', update_data)

    sizing_mode = 'fixed'

    inputs = widgetbox(*wb_controls, sizing_mode=sizing_mode)

    def insert_plot():
        lo.children[0] = make_plot()

    def animate_update():
        mth = slider_month.value + 1
        if mth > max_month:
            mth = 0
        slider_month.value = mth

    def add1():
        slider_val = slider_month.value
        if slider_val < max_month:
            slider_month.value = slider_val + 1

    def sub1():
        slider_val = slider_month.value
        if slider_val > 0:
            slider_month.value = slider_val - 1

    but_1sub.on_click(sub1)
    but_1add.on_click(add1)

    # def slider_update(attrname, old, new):
    #     mth = slider_month.value
    #     label.text = str(mth)
    #     source.data = data[year]

    def animate():
        if play_button.label == '► Play':
            play_button.label = '❚❚ Pause'
            doc.add_periodic_callback(animate_update, 350)
        else:
            play_button.label = '► Play'
            doc.remove_periodic_callback(animate_update)

    def reset():
        slider_month.value = 0

    play_button = Button(label='► Play', width=60)
    play_button.on_click(animate)

    reset_button = Button(label='Reset', width=60)
    reset_button.on_click(reset)

    lo = row(make_plot(), inputs, column(play_button,
                                         reset_button,
                                         add_sub))

    doc.add_root(lo)
