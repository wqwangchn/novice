# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2020/9/16 17:34
Desc:
'''
import gmplot
import webbrowser
import os

# plot the locations on google map  真实经纬度信息
def plot_google_map(data, to_html_name,web_open=False):
    html_name = os.path.abspath(to_html_name)
    assert 'latitude' in data.columns
    assert 'longitude' in data.columns
    latitude_array = data['latitude'].values
    latitude_list = latitude_array.tolist()
    Longitude_array = data['longitude'].values
    longitude_list = Longitude_array.tolist()
    # Initialize the map to the first location in the list
    gmap = gmplot.GoogleMapPlotter(latitude_list[0], longitude_list[0], 10)
    # gmap.scatter(latitude_list, longitude_list, edge_width=10)
    gmap.heatmap(latitude_list, longitude_list)
    # Write the map in an HTML file
    # gmap.draw('Paths_map.html')
    gmap.draw(html_name)
    if web_open:
        webbrowser.open(url='file://' + html_name, new=0, autoraise=True)

if __name__ == '__main__':
    import pandas as pd
    df_raw = pd.DataFrame(data=[[-0.4302744, 35.5331974],
                                [-1.21167, 36.8973031],
                                [0.5217472, 35.255192],
                                [-2.2326433, 38.0769783],
                                [-1.0625246, 34.4734754]],
                          columns=['latitude', 'longitude']
                          )
    plot_google_map(df_raw,"google_apply_map.html",web_open=True)
