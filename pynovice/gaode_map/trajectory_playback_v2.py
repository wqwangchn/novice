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

pattern_headdata=re.compile("var wqadd_headdata = \[\];",re.MULTILINE | re.DOTALL)
pattern_taildata=re.compile("var wqadd_taildata = \[\];",re.MULTILINE | re.DOTALL)
pattern_headfunc=re.compile("var wqadd_headfunc = \[\];",re.MULTILINE | re.DOTALL)
pattern_tailfunc=re.compile("var wqadd_tailfunc = \[\];",re.MULTILINE | re.DOTALL)

pattern_gpslist=re.compile(r"(?<=var lineArr = ).*?(?=;$)",re.MULTILINE | re.DOTALL)
pattern_triplist=re.compile(r"(?<=var tripList = ).*?(?=;$)",re.MULTILINE | re.DOTALL)
pattern_markerlist=re.compile(r"(?<=var markerArr = ).*?(?=;$)",re.MULTILINE | re.DOTALL)
pattern_automarker=re.compile(r"(?<=var auto_marker = ).*?(?=;$)",re.MULTILINE | re.DOTALL)

class Trajectory():
    def __init__(self, lnglat_arr=[], trip_list=[], auto_marker=True):
        self.js=get_main_js()
        self.gps_str = json.dumps(lnglat_arr)
        self.trip_str = json.dumps(trip_list)
        self.marker_str = '[]'
        self.auto_marker = str(auto_marker).lower()
        self.head_data = ''
        self.tail_data = ''
        self.head_func = ''
        self.tail_func = ''
        self.html_name = os.path.abspath('gps_trajectory_playback.html')

    def add_marker(self,marker_arr=[]):
        self.marker_str = json.dumps(marker_arr)


    def add_jsdata(self,data_js='',position='head'):
        assert position in ('head','tail')
        if 'head'==position:
            self.head_data = str(data_js)
        else:
            self.tail_data = str(data_js)

    def add_jsfunc(self,func_js='',position='tail'):
        assert position in ('head','tail')
        if 'head'==position:
            self.head_func = str(func_js)
        else:
            self.tail_func = str(func_js)

    def building(self,html_name=None,web_open=False,speed=200):
        _out1 = re.sub(pattern_gpslist, self.gps_str, self.js)
        _out2 = re.sub(pattern_triplist, self.trip_str, _out1)
        _out3 = re.sub(pattern_markerlist, self.marker_str, _out2)
        _out = _out3
        #
        # _out3 = re.sub(pattern_headdata, self.head_data, _out2)
        # _out4 = re.sub(pattern_taildata, self.tail_data, _out3)
        # _out5 = re.sub(pattern_headfunc, self.head_func, _out4)
        # _out6 = re.sub(pattern_tailfunc, self.tail_func, _out5)
        # _out = re.sub(pattern_automarker, self.auto_marker, _out6)
        # _out = re.sub(pattern_speed, str(speed), _out)
        if html_name:
            self.html_name = os.path.abspath(str(html_name)+'.html')
        dump_data(_data=_out,file_name=self.html_name)
        if web_open:
            webbrowser.open(url='file://' + self.html_name, new=0, autoraise=True)

def get_main_js():
    filename= os.path.abspath('pynovice_map.js')
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

    traj = Trajectory(lnglat_arr=gps_list,trip_list=marker_list,auto_marker=False)
    traj.building(web_open=True,speed=20000)



