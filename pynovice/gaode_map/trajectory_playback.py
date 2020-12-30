# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2020/12/28 15:04
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
pattern_gpslist=re.compile(r"(?<=var marker, lineArr = ).*?(?=;$)",re.MULTILINE | re.DOTALL)
pattern_markerlist=re.compile(r"(?<=var marker_list = ).*?(?=;$)",re.MULTILINE | re.DOTALL)
pattern_automarker=re.compile(r"(?<=var auto_marker = ).*?(?=;$)",re.MULTILINE | re.DOTALL)
pattern_speed=re.compile(r"(?<=var _speed = ).*?(?=;$)",re.MULTILINE | re.DOTALL)

class Trajectory():
    def __init__(self, gps_list=[], marker_list=[], auto_marker=True):
        self.js=get_main_js()
        self.gps_str = json.dumps(gps_list)
        self.marker_str = json.dumps(marker_list)
        self.auto_marker = str(auto_marker).lower()
        self.head_data = ''
        self.tail_data = ''
        self.head_func = ''
        self.tail_func = ''
        self.html_name = os.path.abspath('gps_trajectory_playback.html')

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
        _out2 = re.sub(pattern_markerlist, self.marker_str, _out1)
        _out3 = re.sub(pattern_headdata, self.head_data, _out2)
        _out4 = re.sub(pattern_taildata, self.tail_data, _out3)
        _out5 = re.sub(pattern_headfunc, self.head_func, _out4)
        _out6 = re.sub(pattern_tailfunc, self.tail_func, _out5)
        _out = re.sub(pattern_automarker, self.auto_marker, _out6)
        _out = re.sub(pattern_speed, str(speed), _out)
        if html_name:
            self.html_name = os.path.abspath(str(html_name)+'.html')
        dump_data(_data=_out,file_name=self.html_name)
        if web_open:
            webbrowser.open(url='file://' + self.html_name, new=0, autoraise=True)

def get_main_js():
    main_js = '''
<!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
        <title>轨迹回放</title>
        <link rel="stylesheet" href="https://a.amap.com/jsapi_demos/static/demo-center/css/demo-center.css"/>
        <script src="https://cache.amap.com/lbs/static/es5.min.js"></script>
        <script type="text/javascript" src="https://webapi.amap.com/maps?v=1.4.15&key=d0b0f942970a97389a81d82e505642bf&&plugin=AMap.Scale,AMap.OverView,AMap.ToolBar"></script>
        <style>
            html, body, #container {
                height: 100%;
                width: 100%;
            }
            .input-card .btn{
                margin-right: 1.2rem;
                width: 9rem;
            }
            .input-card .btn:last-child{
                margin-right: 0;
            }
        </style>
    </head>
    <body>
        <div id="container"></div>
        <div class="input-card">
            <h4>轨迹回放控制</h4>
            <div class="input-item">
                <input type="button" class="btn" value="开始动画" id="start" onclick="startAnimation()"/>
                <input type="button" class="btn" value="暂停动画" id="pause" onclick="pauseAnimation()"/>
            </div>
            <div class="input-item">
                <input type="button" class="btn" value="继续动画" id="resume" onclick="resumeAnimation()"/>
                <input type="button" class="btn" value="停止动画" id="stop" onclick="stopAnimation()"/>
            </div>
        </div>
        <script>
            var wqadd_headdata = [];
            var marker, lineArr = [[116.478935,39.997761],[116.478939,39.997825],[116.478912,39.998549],[116.478912,39.998549],[116.478998,39.998555],[116.478998,39.998555],[116.479282,39.99856],[116.479658,39.998528],[116.480151,39.998453],[116.480784,39.998302],[116.480784,39.998302],[116.481149,39.998184],[116.481573,39.997997],[116.481863,39.997846],[116.482072,39.997718],[116.482362,39.997718],[116.483633,39.998935],[116.48367,39.998968],[116.484648,39.999861]];
            if (lineArr.length<1)
            {
                marker_visible=false
            }
            else 
            {
                marker_visible=true
            }
            // 
            var map = new AMap.Map("container", {
                resizeEnable: true,
                center: lineArr[0],
                zoom: 17
            });
            var scale = new AMap.Scale({
                visible: true
            });
            var toolBar = new AMap.ToolBar({
                visible: true
            });
            var overView = new AMap.OverView({
                visible: true
            });
            map.addControl(scale);
            map.addControl(toolBar);
            map.addControl(overView);

            marker = new AMap.Marker({
                map: map,
                position: lineArr[0],
                icon: "https://webapi.amap.com/images/car.png",
                offset: new AMap.Pixel(-26, -13),
                autoRotation: true,
                angle:-90,
                visible:marker_visible,
            });
            // 绘制轨迹
            var polyline = new AMap.Polyline({
                map: map,
                path: lineArr,
                showDir:true,
                strokeColor: "#28F",  //线颜色
                // strokeOpacity: 1,     //线透明度
                strokeWeight: 6,      //线宽
                // strokeStyle: "solid"  //线样式
            });

            var passedPolyline = new AMap.Polyline({
                map: map,
                // path: lineArr,
                strokeColor: "#AF5",  //线颜色
                // strokeOpacity: 1,     //线透明度
                strokeWeight: 6,      //线宽
                // strokeStyle: "solid"  //线样式
            });

            //新增标记点
            var marker_list = [[116.478935,39.997761],[116.484648,39.999861]];
            var auto_marker = true;
            for (var i = 0; i < marker_list.length; i++) {
                var _curData = marker_list[i];
                if (_curData.length>=3)
                {
                    cont_text=(i+1).toString()+": "+_curData[2].toString();
                }
                else
                {   if (auto_marker)
                    {
                        cont_text=(i+1).toString();
                    }
                    else
                    {
                        cont_text='';
                    }     
                }
                var marker_i = new AMap.Marker({position: new AMap.LngLat(_curData[0],_curData[1]),label:{content: cont_text}});
                    map.add(marker_i);
            };
            marker.on('moving', function (e) {
                passedPolyline.setPath(e.passedPath);
            });
            map.setFitView();

            var wqadd_taildata = [];
            var wqadd_headfunc = [];

            function startAnimation () {
                var _speed = 200;
                marker.moveAlong(lineArr, _speed);
            }
            function pauseAnimation () {
                marker.pauseMove();
            }
            function resumeAnimation () {
                marker.resumeMove();
            }
            function stopAnimation () {
                marker.stopMove();
            }

            var wqadd_tailfunc = [];
        </script>
    </body>
</html>
'''
    return main_js

def dump_data(_data, file_name):
    with open(file_name, 'w') as f:
        data_html = f.write(_data)
    print("The output file is downloaded to {}".format(file_name))


if __name__ == '__main__':
    gps_list=[[116.478935,39.997761],[116.478939,39.997825],[116.478912,39.998549],[116.478912,39.998549],[116.478998,39.998555],[116.478998,39.998555],[116.479282,39.99856],[116.479658,39.998528],[116.480151,39.998453],[116.480784,39.998302],[116.480784,39.998302],[116.481149,39.998184],[116.481573,39.997997],[116.481863,39.997846],[116.482072,39.997718],[116.482362,39.997718],[116.483633,39.998935],[116.48367,39.998968],[116.484648,39.999861]]
    marker_list=[[116.478935,39.997761],[116.484648,39.999861]]

    traj = Trajectory(gps_list=gps_list,marker_list=marker_list,auto_marker=False)
    traj.building(web_open=True,speed=20000)



