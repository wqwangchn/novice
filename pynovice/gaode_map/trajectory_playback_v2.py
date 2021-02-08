# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/01/19 15:04
Desc:
'''

import os
import re
import json
import webbrowser

pattern_headdata=re.compile("var add_data = \[\];",re.MULTILINE | re.DOTALL)
pattern_tailfunc=re.compile("var add_func = \{\};",re.MULTILINE | re.DOTALL)

pattern_gpslist=re.compile(r"(?<=var lineArr = ).*?(?=;$)",re.MULTILINE | re.DOTALL)
pattern_triplist=re.compile(r"(?<=var tripList = ).*?(?=;$)",re.MULTILINE | re.DOTALL)
pattern_markerlist=re.compile(r"(?<=var markerSet = ).*?(?=;$)",re.MULTILINE | re.DOTALL)
pattern_showMarker=re.compile(r"(?<=var showMarker = ).*?(?=;$)",re.MULTILINE | re.DOTALL)

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
class Trajectory():
    def __init__(self, lnglat_arr=[], trip_list=[], show_marker=True):
        assert show_marker in (True,False)
        self.js=get_main_js()
        self.gps_str = json.dumps(lnglat_arr)
        self.trip_str = json.dumps(trip_list)
        self.show_marker = str(show_marker).lower()
        self.trip_length=len(trip_list)
        self.marker_set = []
        self.head_data = []
        self.tail_func = []
        self.html_name = os.path.abspath('gps_trajectory_playback.html')

    def add_marker(self,marker_arr=[],marker_img='default'):
        if marker_img == 'default':
            if self.trip_length>0:
                img = "https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png"
            else:
                img = "https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png"
        elif marker_img == 'blue':
            img = "https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png"
        elif marker_img == 'red':
            img="https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png"
        else:
            img=marker_img
        if len(marker_arr)>0:
            self.marker_set.append({
                "data":marker_arr,
                "img":img
            })

    def add_jsdata(self,data_js=''):
        self.head_data.add(str(data_js))

    def add_jsfunc(self,func_js=''):
        self.tail_func.add(str(func_js))

    def building(self,html_name=None,web_open=False):
        _out = re.sub(pattern_gpslist, self.gps_str, self.js)
        _out = re.sub(pattern_triplist, self.trip_str, _out)
        _out = re.sub(pattern_showMarker, self.show_marker, _out)

        if self.marker_set:
            _out = re.sub(pattern_markerlist, json.dumps(self.marker_set), _out)
        _out = re.sub(pattern_headdata, ''.join(self.head_data), _out)
        _out = re.sub(pattern_tailfunc, ''.join(self.tail_func), _out)
        out = _out
        if html_name:
            self.html_name = os.path.abspath(str(html_name)+'.html')
        dump_data(_data=out,file_name=self.html_name)
        if web_open:
            webbrowser.open(url='file://' + self.html_name, new=0, autoraise=True)

def get_main_js():
    filename= os.path.join(CURRENT_PATH,'pynovice_map.js')
    with open(filename,'r') as f:
        main_js = f.read()
    return main_js

def dump_data(_data, file_name):
    with open(file_name, 'w') as f:
        data_html = f.write(_data)
    print("The output file is downloaded to {}".format(file_name))


if __name__ == '__main__':
    gps_list=[[116.478935,39.997761],[116.478939,39.997825],[116.478912,39.998549],[116.478912,39.998549],[116.478998,39.998555],[116.478998,39.998555],[116.479282,39.99856],[116.479658,39.998528],[116.480151,39.998453],[116.480784,39.998302],[116.480784,39.998302],[116.481149,39.998184],[116.481573,39.997997],[116.481863,39.997846],[116.482072,39.997718],[116.482362,39.997718,'info:ttttt'],[116.483633,39.998935,'info:qqqqqqqq'],[116.48367,39.998968,'info:1234254325'],[116.484648,39.999861,'info:dsafaf']]
    marker_list=[3,5,10,15]

    traj = Trajectory(lnglat_arr=gps_list,trip_list=marker_list,show_marker=False)
    traj.add_marker(marker_arr=[[116.478912,39.998549,'akdfjkajfkjaksdf']])
    traj.add_marker(marker_arr=[[116.480784,39.998302]],marker_img='blue')
    traj.building(web_open=True)



