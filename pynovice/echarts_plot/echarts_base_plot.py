# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2021-02-08 18:09
Desc:
map extends
'''

import pandas as pd
import re
import os
from pyecharts.charts import Bar, Line, Page, Grid, Tab
from pyecharts.globals import ThemeType
from pyecharts.components import Table
from pyecharts import options as opts
from pynovice.rule_engine import RuleParser
from pynovice.util import progress_bar

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
def plot_base_bar1(df: pd.DataFrame, title_name='', subtitle_name='', xaxis_name='', yaxis_name='',
                   is_save: bool = False):
    '''
        柱状图
    '''
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)
    if df.columns.size == 1:
        ynames = [df.index.name if yaxis_name == '' else yaxis_name]
        df.columns = ynames
        yaxis_name = ''
    else:
        ynames = df.columns.tolist()
    # plot
    _data = df.copy()
    c1 = Bar({'bg_color':'white'})
    c1.set_global_opts(
        title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
        legend_opts=opts.LegendOpts(is_show=True),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name=xaxis_name),
        yaxis_opts=opts.AxisOpts(name=yaxis_name),
        datazoom_opts=opts.DataZoomOpts(is_show=True)
    )
    c1.add_xaxis([str(i) for i in _data.index)
    for icol in ynames:
        c1.add_yaxis(icol, _data[icol].values.tolist())
    c1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    if is_save:
        return c1
    else:
        return c1.render_notebook()


def plot_base_line1(df: pd.DataFrame, title_name='', subtitle_name='', xaxis_name='', yaxis_name='',
                    is_save: bool = False):
    '''
        折线图
    '''
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)
    if df.columns.size == 1:
        ynames = [df.index.name if yaxis_name == '' else yaxis_name]
        df.columns = ynames
        yaxis_name = ''
    else:
        ynames = df.columns.tolist()
    # plot
    _data = df.copy()
    c1 = Line({'bg_color':'white'})
    c1.set_global_opts(
        title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
        legend_opts=opts.LegendOpts(is_show=True),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name=xaxis_name),
        yaxis_opts=opts.AxisOpts(name=yaxis_name),
        datazoom_opts=opts.DataZoomOpts(is_show=True)
    )
    c1.add_xaxis([str(i) for i in _data.index])
    for icol in ynames:
        c1.add_yaxis(icol, _data[icol].values.tolist())
    c1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    if is_save:
        return c1
    else:
        return c1.render_notebook()

def plot_base_line2(df1: pd.DataFrame, df2: pd.DataFrame,
                    title_name='', subtitle_name='', xaxis_name='', yaxis_name1='', yaxis_name2='',
                    is_save: bool = False):
    '''
    折线图(双坐标)
    '''
    if isinstance(df1, pd.Series):
        df1 = pd.DataFrame(df1)
    if isinstance(df2, pd.Series):
        df2 = pd.DataFrame(df2)
    assert df1.index.to_list()==df2.index.to_list()
    _data1 = df1.copy()
    _data2 = df2.copy()
    # plot
    c1 = Line({'bg_color':'white'})
    c1.set_global_opts(
        title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
        legend_opts=opts.LegendOpts(is_show=True),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name=xaxis_name),
        yaxis_opts=opts.AxisOpts(name=yaxis_name1),
        datazoom_opts=opts.DataZoomOpts(is_show=True)
    )
    c1.extend_axis(yaxis=opts.AxisOpts(name=yaxis_name2,position="right"))
    c1.add_xaxis(_data1.index.tolist())
    for icol in _data1.columns:
        c1.add_yaxis(icol, _data1[icol].values.tolist(),yaxis_index=0)
    for icol in _data2.columns:
        c1.add_yaxis(icol, _data2[icol].values.tolist(),yaxis_index=1)
    c1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    if is_save:
        return c1
    else:
        return c1.render_notebook()

def plot_base_grid1(df1: pd.DataFrame, df2: pd.DataFrame,
                    title_name='', subtitle_name='', xaxis_name='', yaxis_name1='', yaxis_name2='',
                    is_save: bool = False):
    '''
        组合折线图(上下)
    '''
    if isinstance(df1, pd.Series):
        df1 = pd.DataFrame(df1)
    if isinstance(df2, pd.Series):
        df2 = pd.DataFrame(df2)
    len_col = df2.columns.size

    # plot1
    _data = df1.copy()
    c1 = Line({'bg_color':'white'})
    c1.add_xaxis([str(i) for i in _data.index])
    for icol in _data.columns.tolist():
        c1.add_yaxis(str(icol), _data[icol].values.tolist())
    c1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    if (len_col > 5):
        opt_leg = opts.LegendOpts(is_show=True, type_='scroll',
                                  pos_left='25%', pos_right='25%')
    else:
        opt_leg = opts.LegendOpts(is_show=True)
    c1.set_global_opts(
        title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
        legend_opts=opt_leg,
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name=xaxis_name),
        yaxis_opts=opts.AxisOpts(name=yaxis_name1),
        datazoom_opts=opts.DataZoomOpts(is_show=True),
    )
    # plot2
    _data = df2.copy()
    c2 = Line({'bg_color':'white'})
    c2.add_xaxis([str(i) for i in _data.index])
    for icol in _data.columns.tolist():
        c2.add_yaxis(str(icol), _data[icol].values.tolist())
    c2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    c2.set_global_opts(
        legend_opts=opts.LegendOpts(is_show=False),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name=xaxis_name),
        yaxis_opts=opts.AxisOpts(name=yaxis_name2),
    )
    grid = Grid(init_opts=opts.InitOpts(theme="white", bg_color='white', ))
    grid.add(c1, grid_opts=opts.GridOpts(pos_bottom="50%"))
    grid.add(c2, grid_opts=opts.GridOpts(pos_top="65%"))

    if is_save:
        return grid
    else:
        return grid.render_notebook()


if __name__ == '__main__':
    pass