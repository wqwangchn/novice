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
import numpy as np
import reverse_geocoder as rg
import pandas as pd
from pyecharts.datasets import register_url
from pyecharts import options as opts
from pyecharts.charts import Geo,Map,Tab
from pyecharts.globals import ChartType
import json
from pyecharts.components import Table
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
class GeoMap:
    def __init__(self, country='肯尼亚'):
        self.commit = "reverse Geocoder takes a latitude / longitude coordinate and returns the nearest town/city."
        self.df_geo_dict = None
        self.country = country
        self.series_name = country
        self.html_name = os.path.abspath('geo.html')
        self.echarts_url = "https://echarts-maps.github.io/echarts-countries-js/"
        self.geo_dict = {}
        self.init_assert()

    def init_assert(self):
        city_list = self.get_city_list()['CITY(key)'].to_list()
        if '中国' == self.country:
            self.country = 'china'
        elif '印度尼西亚' == self.country:
            self.country = '印度尼西亚, 印尼'
        elif self.country not in city_list:
            print('Get more country|city info, use GeoMap.get_city_list()... ')
        else:
            pass

    def set_out_file(self,html_path):
        self.html_name = os.path.abspath(html_path)

    def get_geo_reverse(self, df_raw):
        '''
        根据经纬度获取 城市信息
        :param df_raw: Dataframe containing latitude and longitude information
        :return: the nearest town/city info
        '''
        assert 'latitude' in df_raw.columns, 'assert latitude in columns'
        assert 'longitude' in df_raw.columns, 'assert longitude in columns'
        df_gps = df_raw[['latitude', 'longitude']].reset_index(drop=True,inplace=False)
        _tuple_gps = df_gps.apply(lambda x: (x['latitude'], x['longitude']), axis=1).to_list()
        _geo_raw = rg.search(_tuple_gps)
        _geo = pd.read_json(json.dumps(_geo_raw))
        df_geo = pd.concat([df_gps, _geo], axis=1)
        self.geo_dict = dict(df_geo.apply(lambda x:(x['admin1'],[x['lon'],x['lat']]),axis=1).values)
        return df_geo

    def plot_geo_summary(self,_geo_data,series_name=None,threshold_plot=None ):
        '''
        plot geo 经纬度聚类信息
        :param geo_data: geo对应的城市分布(Series)
        :return:
        '''
        self.series_name = series_name if series_name else self.series_name

        geo_data = np.array(list(dict(_geo_data).items()))
        self.threshold_plot = np.percentile(_geo_data, 80) if not threshold_plot else threshold_plot
        _geo = self.get_geo_base(geo_data)
        _map = self.get_map_base(geo_data)
        table = self.get_table_base(geo_data)

        tab = Tab(page_title=self.country, )  # 选项卡多图
        tab.add(_map, "VisualMap")
        tab.add(_geo, "HeatMap")
        tab.add(table, "Data")
        tab.render(self.html_name)

    def get_geo_base(self, _data):
        '''
        plot geo-HeatMap
        :param _data: gps对应的城市分布(dataframe)
        :return: geo城市分布图
        '''
        register_url(self.echarts_url)
        geo = Geo(init_opts=opts.InitOpts(width="1000px", height="600px", page_title=self.country, bg_color=''))
        geo.add_schema(maptype=self.country)
        for _city,_gps in self.geo_dict.items():
            geo.add_coordinate(name=_city, longitude=_gps[0], latitude=_gps[1])
        geo.add(series_name = self.series_name, data_pair = _data, type_=ChartType.HEATMAP)
        geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        geo.set_global_opts(visualmap_opts=opts.VisualMapOpts(max_= self.threshold_plot),
                            title_opts=opts.TitleOpts(title="Geo-HeatMap"))
        return geo

    def get_map_base(self, _data):
        '''
        plot geo-VisualMap
        :param _data: gps对应的城市分布(dataframe)
        :return: 热点图
        '''
        register_url(self.echarts_url)
        c_map = Map(init_opts=opts.InitOpts(width="1000px", height="600px", page_title='', bg_color=''))
        c_map.add(series_name=self.series_name, data_pair=_data, maptype=self.country)
        c_map.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        c_map.set_global_opts(title_opts=opts.TitleOpts(title="Map-VisualMap"),
                              visualmap_opts=opts.VisualMapOpts(max_= self.threshold_plot))
        return c_map

    def get_table_base(self,_data):
        '''
        plot geo-detail
        :param _data: gps对应的城市分布(dataframe)
        :return: 数据示例
        '''
        table = Table()
        headers = ["City name", "Number"]
        rows = _data
        table.add(headers, rows).set_global_opts(
            title_opts=opts.ComponentTitleOpts(title="Table-Details")
        )
        return table

    def get_city_list(self):
        df = pd.read_csv(os.path.join(CURRENT_PATH,'CITY.cg'))
        return df

    def run_geo_map(self,df_raw,web_open=False):
        df_gps = self.get_geo_reverse(df_raw)
        geo_data = df_gps.groupby("admin1")['lon'].count()
        self.plot_geo_summary(geo_data)
        if web_open:
            webbrowser.open(url='file://' + self.html_name, new=0, autoraise=True)

if __name__ == '__main__':
    df_raw = pd.DataFrame( data = [[-0.4302744, 35.5331974],
                                   [-1.21167  , 36.8973031],
                                   [ 0.5217472, 35.255192 ],
                                   [-2.2326433, 38.0769783],
                                   [-1.0625246, 34.4734754]],
                           columns=['latitude', 'longitude']
                           )
    geo_map = GeoMap()
    geo_map.run_geo_map(df_raw,web_open=True)