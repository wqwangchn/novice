# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-07-03 17:31
Desc: 规划中，，，，不可用
BMap
Bar
Boxplot
Funnel
Geo
HeatMap
line
bar
Map
Pie
Scatter
WordCloud

图形组件
组合组件


[Bar,Line]
Scatter
HeatMap
'''

import webbrowser
import os
import pandas as pd
from pyecharts.components import Table
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Scatter, Page, Tab, Grid, Timeline,HeatMap

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

class DistributionAnysis:
    def __init__(self):
        self.commit = "Analyze and plot the data "
        self.html_name = os.path.abspath('data_distribution.html')
        self.datas = []

    def add_data(self, _df, chart_type, title_name, subtitle_name='', xname='', yname='', global_opts={},
                 xaxis_opts={}, yaxis_opts={}):
        chart = self.check_chart(chart_type)
        chart.set_global_opts(title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15), name=xname),  # label旋转
                            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}"), name=yname),
                            datazoom_opts=opts.DataZoomOpts(),  # 滑动条
                            toolbox_opts=opts.ToolboxOpts(),
                            **global_opts
                            )
        xaxis = list(map(str, _df.index))
        chart.add_xaxis(xaxis,**xaxis_opts)
        for field in _df.columns:
            chart.add_yaxis(series_name=str(field), yaxis_data=_df[str(field)].to_list(),**yaxis_opts)
        self.datas.append(chart)
        return chart

    def extend_data(self, _df, chart_type, xname='', yname='', xaxis_opts={}, yaxis_opts={},extend_opts={}):
        chart = self.check_chart(chart_type)
        xaxis = list(map(str, _df.index))
        chart.add_xaxis(xaxis,**xaxis_opts)
        for field in _df.columns:
            chart.add_yaxis(series_name=str(field), y_axis=_df[str(field)].to_list(),**yaxis_opts)
        chart.extend_axis(yaxis=opts.AxisOpts(yname=yname, position="right",splitline_opts=opts.SplitLineOpts(
                            is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1))),**extend_opts)
        raw_chart = self.datas[-1]
        new_chart = raw_chart.overlap(chart)
        self.datas[-1] = new_chart
        return chart

    def plot_summary(self,html_name=None,web_open=False,page_type='page',init_opts={},page_opts={}):
        if html_name:
            self.html_name = os.path.abspath(str(html_name)+'.html')

        assert page_type in ('grid', 'page', 'tab', 'timeline'), \
            '仅支持并行多图(grid),单页多图(page),选项卡多图(tab),时间线轮播多图(timeline)'

        if 'grid' == page_type:
            grid = Grid(**init_opts)  # 并行多图
            for idata in self.datas:
                grid.add(idata,**page_opts)
                grid.render(self.html_name)

        if 'page' == page_type:
            page = Page(**init_opts)  # 单页多图
            for idata in self.datas:
                page.add(idata,**page_opts)
                page.render(self.html_name)

        if 'tab' == page_type:
            tab = Tab(**init_opts)  # 选项卡多图
            for idata in self.datas:
                tab.add(idata,**page_opts)
                tab.render(self.html_name)

        if 'timeline' == page_type:
            timeline = Timeline(**init_opts)  # 时间线轮播多图
            for idata in self.datas:
                timeline.add(idata,**page_opts)
                timeline.render(self.html_name)

        if web_open:
            webbrowser.open(url='file://' + self.html_name, new=0, autoraise=True)

    def check_type(self,page_type):
        assert page_type in ('grid', 'page', 'tab', 'timeline'), \
            '仅支持并行多图(grid),单页多图(page),选项卡多图(tab),时间线轮播多图(timeline)'
        self.page_type=page_type

    def check_chart(self, chart_type):
        if isinstance(chart_type,str):
            assert chart_type in ('bar','line','scatter'), '仅支持bar|line|scatter字符定义，特殊chart需输入clas原型'
            if 'bar'==chart_type:
                return Bar()
            elif 'line'==chart_type:
                return Line()
            elif 'scatter'==chart_type:
                return Scatter()
        elif isinstance(chart_type,classmethod):
            return chart_type
        else:
            assert chart_type in ('bar','line','scatter'), '仅支持bar|line|scatter字符定义，特殊chart需输入clas原型'


class WqTab(Tab):
    def __init__(self, page_title: str = CurrentConfig.PAGE_TITLE, js_host: str = ""):
        super().__init__(page_title=page_title,js_host=js_host)


if __name__ == '__main__':
    df_raw = pd.DataFrame( data = [[-0.4302744, 35.5331974],
                                   [-1.21167  , 36.8973031],
                                   [ 0.5217472, 35.255192 ],
                                   [-2.2326433, 38.0769783],
                                   [-1.0625246, 34.4734754]],
                           columns=['latitude', 'longitude'])

    any = DistributionAnysis()
    any.add_data(_df=df_raw,title_name='aa1', subtitle_name='aa',chart_type='bar',yname='xname',xname='yname')
    any.add_data(_df=df_raw,title_name='bb1', subtitle_name='bb',chart_type='line')
    any.plot_summary(web_open=True,html_name=None,afdasf=23)

    a=Bar()
    a.add_js_funcs()
