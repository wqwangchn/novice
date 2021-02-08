# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-16 18:09
Desc:
map extends
'''
import webbrowser
import os
import pandas as pd
from pyecharts.components import Table
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Tab, Page,Grid

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
class DistributionAnysis:
    def __init__(self, image_separation=False):
        self.commit = "Analyze and plot the data "
        self.series_name_add = '_' if image_separation else ''
        self.html_name = os.path.abspath('data_distribution.html')
        self.datas = []

    def get_plot_base(self, _df, title_name='数据分布', subtitle_name='',chart_type=None,xname=None,yname=None):
        '''
        plot line & bar info
        :param _df:
        :return:
        '''
        bar = Bar()
        line = Line()
        bar.set_global_opts(title_opts=opts.TitleOpts(title=title_name, subtitle=subtitle_name),
                            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}"),name=yname),
                            datazoom_opts=opts.DataZoomOpts(),  # 滑动条
                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15),name=xname),  # label旋转
                            toolbox_opts=opts.ToolboxOpts(),
                            )
        xaxis = list(map(str, _df.index))
        bar.add_xaxis(xaxis)
        line.add_xaxis(xaxis)
        for field in _df.columns:
            field=str(field)
            if chart_type=='line':
                line.add_yaxis(series_name=field, y_axis=_df[field].to_list(),is_symbol_show=False)
            elif chart_type=='bar':
                bar.add_yaxis(series_name=field, yaxis_data=_df[field].to_list(), is_selected=True,)
            else:
                bar.add_yaxis(series_name=field, yaxis_data=_df[field].to_list(), is_selected=True)
                line.add_yaxis(series_name=field+self.series_name_add, y_axis=_df[field].to_list(), is_symbol_show=True)
        bar.overlap(line)
        return bar

    def get_table_base(self, _df, title_name='数据分布', subtitle_name=''):
        '''
        数据详情表 （未使用）
        :param _df:
        :param title_name:
        :param subtitle_name:
        :return:
        '''
        _df = _df.reset_index()
        table = Table()
        headers = _df.columns.tolist()
        rows = _df.values
        table.add(headers, rows).set_global_opts(
            title_opts=opts.ComponentTitleOpts(title="Table-{}".format(title_name), subtitle=subtitle_name)
        )
        return table

    def add_data(self,_df,title_name, subtitle_name='',chart_type=None,xname=None,yname=None):
        _plot = self.get_plot_base(_df, title_name, subtitle_name,chart_type,xname,yname)
        self.datas.append(_plot)

    def plot_summary(self,page_name='',page_type='page',web_open=False,html_name=None):
        assert page_type in ('page','tab'),'仅支持单页多图(page)和选项卡多图(tab)'
        if html_name:
            self.html_name = os.path.abspath(str(html_name)+'.html')
        if 'page' == page_type:
            page = Page(page_title=page_name)  # 单页多图
            for idata in self.datas:
                page.add(idata)
                page.render(self.html_name)
        else:
            tab = Tab(page_title=page_name, )  # 选项卡多图
            for idata in self.datas:
                tab_name = idata.options.get('title').opts[0].get('text')
                tab.add(idata,tab_name)
                tab.render(self.html_name)
        if web_open:
            webbrowser.open(url='file://' + self.html_name, new=0, autoraise=True)

if __name__ == '__main__':
    df_raw = pd.DataFrame( data = [[-0.4302744, 35.5331974],
                                   [-1.21167  , 36.8973031],
                                   [ 0.5217472, 35.255192 ],
                                   [-2.2326433, 38.0769783],
                                   [-1.0625246, 34.4734754]],
                           columns=['latitude', 'longitude'])

    any = DistributionAnysis(image_separation=True)
    any.add_data(_df=df_raw,title_name='aa1', subtitle_name='aa',chart_type='bar',yname='xname',xname='yname')
    any.add_data(_df=df_raw,title_name='bb1', subtitle_name='bb')
    any.plot_summary(page_name='1234',page_type='tab',web_open=False,html_name=None)