# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-04-17 11:52
Desc:
'''
import pandas as pd
from pynovice.geo_map import GeoMap
import webbrowser

if __name__ == '__main__':
    df_raw = pd.DataFrame(data= [[-0.4302744, 35.5331974],
                                   [-1.21167  , 36.8973031],
                                   [ 0.5217472, 35.255192 ],
                                   [-2.2326433, 38.0769783],
                                   [-1.0625246, 34.4734754]],
                           columns=['latitude', 'longitude']
                           )
    geo_map = GeoMap()
    geo_map.set_out_file(html_path='../data/geo.html')

    # 全流程运行
    # geo_map.run_geo_map(df_raw,web_open=True)

    # 详细的流程
    df_gps = geo_map.get_geo_reverse(df_raw) #获取geo
    geo_data = df_gps.groupby("admin1")['lon'].count() #要画图的数据 serios
    geo_map.plot_geo_summary(geo_data) #生成geo.html 文件
    webbrowser.open(url='file://' + geo_map.html_name, new=0, autoraise=True) #浏览器打开geo.html文件