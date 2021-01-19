
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
    <title>pynovice_map</title>
    <link rel="stylesheet" href="https://a.amap.com/jsapi_demos/static/demo-center/css/demo-center.css"/>
    <script src="https://cache.amap.com/lbs/static/es5.min.js"></script>
    <script type="text/javascript" src="https://webapi.amap.com/maps?v=1.4.15&key=d0b0f942970a97389a81d82e505642bf&&plugin=AMap.Scale,AMap.OverView,AMap.ToolBar,ElasticMarker"></script>
    <style>
        html, body, #container {
            height: 100%;
            width: 100%;
        }
    </style>
</head>

<body>
    <div id="container"></div>
    <div class="info" id="location_text">
        鼠标点击位置：[lng_mars,lat_mars]
    </div>
    <div class="input-card">
        <style>
            body
            .input-card .btn{
                margin-right: 0.7rem;
                width: 6rem;
            }
            .input-card .btn:last-child{
                margin-right: 0;
            }
        </style>
        <h4>轨迹回放控制</h4>
        <div class="input-item">
            速度： <input type="text" value=200 id="speed">&nbsp;&nbsp;
            行程： <input type="text" value=[0,1] id="stroke">
        </div>
        <div class="input-item">
            <input type="submit" class="btn" value="开始动画" id="resume" onclick="startAnimation()"/>
            <input type="button" class="btn" value="停止动画" id="stroke" onclick="pauseAnimation()"/>
            <input type="submit" class="btn" value="继续动画" id="resume" onclick="resumeAnimation()"/>
        </div>
    </div>

    //data
    <script>
        var lineArr = [[116.478935, 39.997761, "2020-10-02 00:02:38\uff1a\u901f\u5ea646km/h"], [116.478939, 39.997825], [116.478912, 39.998549], [116.478912, 39.998549], [116.478998, 39.998555], [116.478998, 39.998555], [116.479282, 39.99856], [116.479658, 39.998528, "fdafasfdasfasf"], [116.480151, 39.998453], [116.480784, 39.998302], [116.480784, 39.998302], [116.481149, 39.998184], [116.481573, 39.997997], [116.481863, 39.997846], [116.482072, 39.997718], [116.482362, 39.997718, "fdafasfdasfasf"], [116.483633, 39.998935, "fdafasfdasfasf"], [116.48367, 39.998968, "fdafasfdasfasf"], [116.484648, 39.999861, "2020-10-02 00:02:38\uff1a\u901f\u5ea646km/h"]];
        var tripList = [3, 5, 10, 15];
        var markerArr = [[116.478998, 39.998555], [116.478998, 39.998555]];
        // extends
        var massArr = lineArr.concat([]);
        var tripArr=[];
        for (i=0;i<tripList.length;i++){
            tripArr[i]=lineArr[tripList[i]];
        }
    </script>

    // main_container
    <script>
        // function initContainer(){
        var map = new AMap.Map("container", {
            resizeEnable: true,
            center: lineArr.concat(markerArr)[0],
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

        function showInfoClick(e){
            var text = '鼠标点击位置：[ '+e.lnglat.getLng()+','+e.lnglat.getLat()+' ]'
            document.querySelector("#location_text").innerText = text;
        }
        map.on('click', showInfoClick);

        document.getElementById("stroke").value='['+[0,tripList.length+1].toString( )+']';
    </script>

    // trip_marker
    <script>
        var infoWindow = new AMap.InfoWindow({offset: new AMap.Pixel(0, -30)});
        for (var i = 0; i < tripArr.length; i++) {
            var _curData = tripArr[i];
            var _marker = new AMap.Marker({
                position: _curData.slice(0,2),
                map: map
            });
            _marker.content= (i+1).toString()+". "+_curData.slice(2,).toString();
            _marker.on('click', markerClick);
        }
        function markerClick(e) {
            infoWindow.setContent(e.target.content);
            infoWindow.open(map, e.target.getPosition());
        };
    </script>

    // trajectory moving
    <script>
        var marker_moving = new AMap.Marker({
            map: map,
            position: lineArr[0],
            icon: "https://webapi.amap.com/images/car.png",
            offset: new AMap.Pixel(-26, -13),
            autoRotation: true,
            angle:-90
        });

        // 全部轨迹
        var polyline = new AMap.Polyline({
            map: map,
            path: lineArr,
            showDir:true,
            strokeColor: "#BG3",  //线颜色
            strokeOpacity: 0.5,     //线透明度
            strokeWeight: 3,      //线宽
            // strokeStyle: "solid"  //线样式
        });
        // 当前轨迹
        var polyline2 = new AMap.Polyline({
            map: map,
            path: lineArr,
            showDir:true,
            strokeColor: "#28F",  //线颜色
            strokeOpacity: 1,     //线透明度
            strokeWeight: 6,      //线宽
            // strokeStyle: "solid"  //线样式
        });
        // 当前行驶经过的轨迹
        var passedPolyline = new AMap.Polyline({
            map: map,
            strokeColor: "#AF5",  //线颜色
            //strokeOpacity: 1,     //线透明度
            strokeWeight: 6,      //线宽
            // strokeStyle: "solid"  //线样式
        });

        // 当前数据明细
        var mass_style = {
                url: 'https://a.amap.com/jsapi_demos/static/images/mass1.png',
                anchor: new AMap.Pixel(6, 6),
                size: new AMap.Size(6, 6)
        }
        var linemarker = new AMap.Marker({content: ' ', map: map});
        mass = new AMap.MassMarks(null, {
            opacity: 0.4,
            zIndex: 111,
            cursor: 'pointer',
            style: mass_style
        });
        mass.setMap(map);


        function startAnimation () {
            var speed = document.getElementById("speed").value;
            var stroke = checkStroke(document.getElementById("stroke").value);
            updateAnimation(speed,stroke)
        }
        function pauseAnimation () {
            marker_moving.pauseMove();
        }
        function resumeAnimation () {
            marker_moving.resumeMove();
        }

        function checkStroke(stroke){
            if (stroke.trim()==''){
                stroke='['+[0,tripList.length+1].toString( )+']';
            }
            else if(eval(stroke).slice(-1)>tripList.length+1){
                stroke='['+[0,tripList.length+1].toString( )+']';
            }
            else{
                stroke=stroke.toString()
            }
            document.getElementById("stroke").value=stroke
            return eval(stroke)
        };

        function updateAnimation(speed=200,stroke=[0,1]){
            var lineArr_cur = lineArr.slice(tripList[stroke[0]-1],tripList[stroke.slice(-1)-1]);
            var massdata = massArr.slice(tripList[stroke[0]-1],tripList[stroke.slice(-1)-1]);
            var mass_data=[];
            for (var i=0;i<massdata.length;i++){
                mass_data[i]={'lnglat':massdata[i].slice(0, 2),'info':massdata[i].slice(2,)[0]}
            };

            // 当前轨迹
            map.remove(polyline2);
            polyline2 = new AMap.Polyline({
                map: map,
                path: lineArr_cur,
                showDir:true,
                strokeColor: "#28F",  //线颜色
                strokeOpacity: 1,     //线透明度
                strokeWeight: 6,      //线宽
                // strokeStyle: "solid"  //线样式
            });
            // 当前行驶经过的轨迹
            map.remove(passedPolyline);
            passedPolyline = new AMap.Polyline({
                map: map,
                strokeColor: "#AF5",  //线颜色
                //strokeOpacity: 1,     //线透明度
                strokeWeight: 6,      //线宽
                // strokeStyle: "solid"  //线样式
            });
            map.setFitView(polyline2);
            map.setCenter(lineArr_cur[0]);
            marker_moving.position=lineArr_cur[0];
            marker_moving.on('moving', function (e) {
                passedPolyline.setPath(e.passedPath);
            });
            marker_moving.moveAlong(lineArr_cur, speed);

            //当前行程明细数据
            map.remove(mass);
            mass = new AMap.MassMarks(mass_data, {
                opacity: 0.4,
                zIndex: 111,
                cursor: 'pointer',
                style: mass_style
            });
            mass.on('mouseover', function (e) {
                linemarker.setPosition(e.data.lnglat);
                linemarker.setLabel({content: e.data.info})
            });
            mass.setMap(map);

        };
    </script>

    // markerArr
    <script>
        var infoWindow2 = new AMap.InfoWindow({offset: new AMap.Pixel(0, -30)});
        for (var i = 0; i < markerArr.length; i++) {
            var _curData = markerArr[i];
            var _marker = new AMap.Marker({
                position: _curData.slice(0,2),
                icon:'//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png',
                map: map
            });
            _marker.content= _curData.slice(2,).toString();
            _marker.on('click', markerClick);
        }
        function markerClick(e) {
            infoWindow2.setContent(e.target.content);
            infoWindow2.open(map, e.target.getPosition());
        };
    </script>

    // 灵活标记点大小
    <!-- <script>
        var zoomStyleMapping = {
                14:0,
                15:0,
                16:1,
                17:1,
                18:1,
                19:1,
                20:1
        }
        var infoWindow2 = new AMap.InfoWindow({offset: new AMap.Pixel(0, -30)});
        for (var i = 0; i < markerArr.length; i++) {
            var _curData = markerArr[i];
            var marker = new AMap.ElasticMarker({
                position:_curData.slice(0,2),
            styles:[{
                    icon:{
                        img:'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
                        size:[16,16],//可见区域的大小
                        ancher:[8,16],//锚点
                        fitZoom:14,//最合适的级别
                        scaleFactor:1,//地图放大一级的缩放比例系数
                    }
                },{
                    icon:{
                        img:'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
                        size:[6,6],
                        ancher:[8,16],//锚点
                        fitZoom:17.5,
                        scaleFactor:1.2,
                        maxScale:2,
                        minScale:0.125
                    }
                }],
            zoomStyleMapping:zoomStyleMapping
        })
        map.add(marker);
        _marker.content= _curData.slice(2,).toString();
        _marker.on('click', markerClick);
    };
    function markerClick(e) {
            infoWindow2.setContent(e.target.content);
            infoWindow2.open(map, e.target.getPosition());
        };

    </script> -->

    <script>
            map.setFitView();
    </script>
</body>
</html>