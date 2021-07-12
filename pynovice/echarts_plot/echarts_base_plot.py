# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2021-02-08 18:09
Desc:
map extends
base图：
    1.折线图
    2.柱状图
    3.树图(pass)
    4.地图(日历图)
    5.桑基图(数据流转)
    6.热力图
    7.关系图
组合图：
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

def get_kde(x,data_array,bandwidth=0.1):
    '''
    核密度函数
    :param x:
    :param data_array:
    :param bandwidth:
    :return:
    '''
    def gauss(x):
        import math
        return (1/math.sqrt(2*math.pi))*math.exp(-0.5*(x**2))
    N=len(data_array)
    res=0
    if len(data_array)==0:
        return 0
    for i in range(len(data_array)):
        res += gauss((x-data_array[i])/bandwidth)
    res /= (N*bandwidth)
    return res

def clac_kde_fit_tmp(arr_x,bins=50):
    '''
    密度拟合分布(del)
    :param arr_x:
    :param bins:
    :return:
    '''
    bins = min(len(arr_x),bins)
    bandwidth=1.05*np.std(arr_x)*(len(arr_x)**(-1/5))
    x_data = np.linspace(min(arr_x),max(arr_x),bins)
    y_data = pd.cut(arr_x,bins).value_counts().sort_index().tolist()
    y_fit_data = [get_kde(x_data[i],arr_x,bandwidth) for i in range(x_data.shape[0])]
    return x_data,y_data,y_fit_data

def clac_kde_fit(arr_x,bins_list):
    '''
    密度拟合分布
    '''
    bandwidth=1.05*np.std(arr_x)*(len(arr_x)**(-1/5))
    y_data = [get_kde(bins_list[i],arr_x,bandwidth) for i in range(len(bins_list))]
    y_data = [x / sum(y_data) for x in y_data]
    return y_data


def plot_base_bar1(df: pd.DataFrame, title_name='', subtitle_name='', xaxis_name='', yaxis_name='',
                   stack_type=False,is_show_label=False, is_plot: bool = True):
    '''
        柱状图
    '''
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)
    # plot
    _data = df.copy()
    _data.index = [str(i) for i in _data.index]
    c1 = Bar({'bg_color':'white'})
    c1.add_xaxis(_data.index.tolist())
    for icol in _data.columns:
        if stack_type:
            c1.add_yaxis(icol, _data[icol].values.tolist(),stack='stack1')
        else:
            c1.add_yaxis(icol, _data[icol].values.tolist())
    c1.set_global_opts(
        title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
        legend_opts=opts.LegendOpts(is_show=True),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name=xaxis_name),
        yaxis_opts=opts.AxisOpts(name=yaxis_name),
        datazoom_opts=opts.DataZoomOpts(is_show=True)
    )
    c1.set_series_opts(label_opts=opts.LabelOpts(is_show=is_show_label))
    if is_plot:
        return c1.render_notebook()
    else:
        return c1


def plot_base_line1(df: pd.DataFrame, title_name='', subtitle_name='', xaxis_name='', yaxis_name='',
                    is_show_label=False, is_plot: bool = True):
    '''
        折线图
    '''
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)
    # plot
    _data = df.copy()
    _data.index = [str(i) for i in _data.index]
    c1 = Line({'bg_color':'white'})
    c1.add_xaxis(_data.index.tolist())
    for icol in _data.columns:
        c1.add_yaxis(icol, _data[icol].values.tolist())
    c1.set_global_opts(
        title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
        legend_opts=opts.LegendOpts(is_show=True),
        toolbox_opts=opts.ToolboxOpts(is_show=True),
        xaxis_opts=opts.AxisOpts(name=xaxis_name),
        yaxis_opts=opts.AxisOpts(name=yaxis_name),
        datazoom_opts=opts.DataZoomOpts(is_show=True)
    )
    c1.set_series_opts(label_opts=opts.LabelOpts(is_show=is_show_label))
    if is_plot:
        return c1.render_notebook()
    else:
        return c1

def plot_base_grid1(chart1_top, chart_buttom,is_plot: bool = True):
    '''
        组合折线图(上下)
    '''
    grid = Grid(init_opts=opts.InitOpts(theme="white", bg_color='white', ))
    grid.add(chart1_top, grid_opts=opts.GridOpts(pos_bottom="50%"))
    grid.add(chart_buttom, grid_opts=opts.GridOpts(pos_top="65%"))

    if is_plot:
        return grid.render_notebook()
    else:
        return grid

def plot_base_grid2(df1: pd.DataFrame, df2: pd.DataFrame,chart_type='barline',stack_type='FalseFalse',
                    title_name='', subtitle_name='', xaxis_name='', yaxis_name1='', yaxis_name2='',
                    is_plot: bool = True):
    '''
    折线图(双坐标)
    '''
    assert chart_type in ('barbar','lineline','barline','linebar')
    assert stack_type in ('FalseFalse','TrueFalse','TrueTrue','FalseTrue')
    if isinstance(df1, pd.Series):
        df1 = pd.DataFrame(df1)
    if isinstance(df2, pd.Series):
        df2 = pd.DataFrame(df2)
    assert df1.index.to_list()==df2.index.to_list()
    _data1 = df1.copy()
    _data2 = df2.copy()
    # plot
    if chart_type in ('barline','barbar'):
        c1 = Bar({'bg_color':'white'})
    else:
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
    c1.add_xaxis([str(i) for i in _data1.index])
    for icol in _data1.columns:
        if stack_type in ('FalseFalse','FalseTrue'):
            c1.add_yaxis(icol, _data1[icol].values.tolist(),yaxis_index=0)
        else:
            c1.add_yaxis(icol, _data1[icol].values.tolist(),yaxis_index=0,stack='stack1')
    if chart_type in ('lineline','barline'):
        c2 = Line()
    else:
        c2 = Bar()
    c2.add_xaxis([str(i) for i in _data1.index])
    for icol in _data2.columns:
        if stack_type in ('FalseFalse','TrueFalse'):
            c2.add_yaxis(icol, _data2[icol].values.tolist(),yaxis_index=1)
        else:
            c2.add_yaxis(icol, _data2[icol].values.tolist(),yaxis_index=1,stack='stack1')
    c1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    c2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    c1.overlap(c2)
    if is_plot:
        return c1.render_notebook()
    else:
        return c1

# def plot_base_line2(df1: pd.DataFrame, df2: pd.DataFrame,
#                     title_name='', subtitle_name='', xaxis_name='', yaxis_name1='', yaxis_name2='',
#                     is_save: bool = False):
#     '''
#     折线图(双坐标)
#     '''
#     if isinstance(df1, pd.Series):
#         df1 = pd.DataFrame(df1)
#     if isinstance(df2, pd.Series):
#         df2 = pd.DataFrame(df2)
#     assert df1.index.to_list()==df2.index.to_list()
#     _data1 = df1.copy()
#     _data2 = df2.copy()
#     # plot
#     c1 = Line({'bg_color':'white'})
#     c1.set_global_opts(
#         title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
#         legend_opts=opts.LegendOpts(is_show=True),
#         toolbox_opts=opts.ToolboxOpts(is_show=True),
#         xaxis_opts=opts.AxisOpts(name=xaxis_name),
#         yaxis_opts=opts.AxisOpts(name=yaxis_name1),
#         datazoom_opts=opts.DataZoomOpts(is_show=True)
#     )
#     c1.extend_axis(yaxis=opts.AxisOpts(name=yaxis_name2,position="right"))
#     c1.add_xaxis([str(i) for i in _data1.index])
#     for icol in _data1.columns:
#         c1.add_yaxis(icol, _data1[icol].values.tolist(),yaxis_index=0)
#     for icol in _data2.columns:
#         c1.add_yaxis(icol, _data2[icol].values.tolist(),yaxis_index=1)
#     c1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#     if is_save:
#         return c1
#     else:
#         return c1.render_notebook()
#
# def plot_base_barline1(df1: pd.DataFrame, df2: pd.DataFrame,
#                     title_name='', subtitle_name='', xaxis_name='', yaxis_name1='', yaxis_name2='',
#                     is_save: bool = False):
#     '''
#     折线图(双坐标)
#     '''
#     if isinstance(df1, pd.Series):
#         df1 = pd.DataFrame(df1)
#     if isinstance(df2, pd.Series):
#         df2 = pd.DataFrame(df2)
#     assert df1.index.to_list()==df2.index.to_list()
#     _data1 = df1.copy()
#     _data2 = df2.copy()
#     # plot
#     c1 = Bar({'bg_color':'white'})
#     c1.set_global_opts(
#         title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
#         legend_opts=opts.LegendOpts(is_show=True),
#         toolbox_opts=opts.ToolboxOpts(is_show=True),
#         xaxis_opts=opts.AxisOpts(name=xaxis_name),
#         yaxis_opts=opts.AxisOpts(name=yaxis_name1),
#         datazoom_opts=opts.DataZoomOpts(is_show=True)
#     )
#     c1.extend_axis(yaxis=opts.AxisOpts(name=yaxis_name2,position="right"))
#     c1.add_xaxis([str(i) for i in _data1.index])
#     for icol in _data1.columns:
#         c1.add_yaxis(icol, _data1[icol].values.tolist(),yaxis_index=0)
#     c2=Line()
#     c2.add_xaxis([str(i) for i in _data1.index])
#     for icol in _data2.columns:
#         c2.add_yaxis(icol, _data2[icol].values.tolist(),yaxis_index=1)
#     c1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#     c2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#     c1.overlap(c2)
#     if is_save:
#         return c1
#     else:
#         return c1.render_notebook()

# def plot_base_grid1(df1: pd.DataFrame, df2: pd.DataFrame,
#                     title_name='', subtitle_name='', xaxis_name='', yaxis_name1='', yaxis_name2='',
#                     is_save: bool = False):
#     '''
#         组合折线图(上下)
#     '''
#     if isinstance(df1, pd.Series):
#         df1 = pd.DataFrame(df1)
#     if isinstance(df2, pd.Series):
#         df2 = pd.DataFrame(df2)
#     len_col = df2.columns.size
#
#     # plot1
#     _data = df1.copy()
#     c1 = Line({'bg_color':'white'})
#     c1.add_xaxis([str(i) for i in _data.index])
#     for icol in _data.columns.tolist():
#         c1.add_yaxis(str(icol), _data[icol].values.tolist())
#     c1.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#     if (len_col > 5):
#         opt_leg = opts.LegendOpts(is_show=True, type_='scroll',
#                                   pos_left='25%', pos_right='25%')
#     else:
#         opt_leg = opts.LegendOpts(is_show=True)
#     c1.set_global_opts(
#         title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
#         legend_opts=opt_leg,
#         toolbox_opts=opts.ToolboxOpts(is_show=True),
#         xaxis_opts=opts.AxisOpts(name=xaxis_name),
#         yaxis_opts=opts.AxisOpts(name=yaxis_name1),
#         datazoom_opts=opts.DataZoomOpts(is_show=True),
#     )
#     # plot2
#     _data = df2.copy()
#     c2 = Line({'bg_color':'white'})
#     c2.add_xaxis([str(i) for i in _data.index])
#     for icol in _data.columns.tolist():
#         c2.add_yaxis(str(icol), _data[icol].values.tolist())
#     c2.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#     c2.set_global_opts(
#         legend_opts=opts.LegendOpts(is_show=False),
#         toolbox_opts=opts.ToolboxOpts(is_show=True),
#         xaxis_opts=opts.AxisOpts(name=xaxis_name),
#         yaxis_opts=opts.AxisOpts(name=yaxis_name2),
#     )
#     grid = Grid(init_opts=opts.InitOpts(theme="white", bg_color='white', ))
#     grid.add(c1, grid_opts=opts.GridOpts(pos_bottom="50%"))
#     grid.add(c2, grid_opts=opts.GridOpts(pos_top="65%"))
#
#     if is_save:
#         return grid
#     else:
#         return grid.render_notebook()


if __name__ == '__main__':
    pass