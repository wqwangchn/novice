
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


    <script>
        var lineArr = [[116.478935,39.997761,'info1'],[116.478939,39.997825,'info2'],[116.478912,39.998549],[116.478912,39.998549],[116.478998,39.998555],[116.478998,39.998555],[116.479282,39.99856],[116.479658,39.998528],[116.480151,39.998453,'info3'],[116.480784,39.998302],[116.480784,39.998302],[116.481149,39.998184],[116.481573,39.997997],[116.481863,39.997846],[116.482072,39.997718],[116.482362,39.997718],[116.483633,39.998935,'info4'],[116.48367,39.998968],[116.484648,39.999861]];
        var markerArr=[];
        var tripArr=[3,5,8,10,12,17,19];
        var massArr=lineArr.concat([]);
    </script>


    <script>
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
    </script>

    <script>
        var marker_moving = new AMap.Marker({
                map: map,
                position: lineArr[0],
                icon: "https://webapi.amap.com/images/car.png",
                offset: new AMap.Pixel(-26, -13),
                autoRotation: true,
                angle:-90
            });
        var polyline = new AMap.Polyline({
            map: map,
            path: lineArr,
            showDir:true,
            strokeColor: "#BG3",  //线颜色
            strokeOpacity: 0.5,     //线透明度
            strokeWeight: 3,      //线宽
            // strokeStyle: "solid"  //线样式
        });
        var polyline2 = new AMap.Polyline({
            map: map,
            path: null,
            showDir:true,
            strokeColor: "#28F",  //线颜色
            strokeOpacity: 1,     //线透明度
            strokeWeight: 6,      //线宽
            // strokeStyle: "solid"  //线样式
        });
        var passedPolyline = new AMap.Polyline({
            map: map,
            strokeColor: "#AF5",  //线颜色
            //strokeOpacity: 1,     //线透明度
            strokeWeight: 6,      //线宽
            // strokeStyle: "solid"  //线样式
        });

        document.getElementById("stroke").value='['+[0,tripArr.length].toString( )+']';
        function initAnimation(lineArr_main,speed=200,stroke=[0,1]){
            var lineArr_main=lineArr.slice(tripArr[stroke[0]-1],tripArr[stroke.slice(-1)-1]);
            marker_moving.position=lineArr_main[0];
            polyline2.path=lineArr_main;
            marker_moving.on('moving', function (e) {
                passedPolyline.setPath(e.passedPath);
            });
            marker_moving.moveAlong(lineArr_main, speed );
        }

        function startAnimation () {
            var speed = document.getElementById("speed").value;
            var stroke = document.getElementById("stroke").value;
            if (stroke.trim()==''){
                stroke='['+[0,tripArr.length].toString( )+']';
                document.getElementById("stroke").value=stroke
            }
            else{
                stroke=eval(stroke)
            }
            if (stroke.slice(-1)>tripArr.length){
                document.getElementById("stroke").value='['+[0,tripArr.length].toString( )+']';
            }
            initAnimation(lineArr,speed,stroke)
        }
        function pauseAnimation () {
            marker_moving.pauseMove();
        }
        function resumeAnimation () {
            marker_moving.resumeMove();
        }

</script>

<script>
    var mass_data=[];
    for (var i=0;i<massArr.length;i++){
        mass_data[i]={'lnglat':massArr[i].slice(0, 2),'info':massArr[i].slice(2,)[0]}
    }
    var style = {
            url: 'https://a.amap.com/jsapi_demos/static/images/mass1.png',
            anchor: new AMap.Pixel(6, 6),
            size: new AMap.Size(6, 6)
        }
    var mass = new AMap.MassMarks(mass_data, {
        opacity: 0.4,
        zIndex: 111,
        cursor: 'pointer',
        style: style
    });
    var linemarker = new AMap.Marker({content: ' ', map: map});
    mass.on('mouseover', function (e) {
        linemarker.setPosition(e.data.lnglat);
        linemarker.setLabel({content: e.data.info})
    });
    mass.setMap(map);
</script>

<script>
        map.setFitView();
</script>
</body>
</html>