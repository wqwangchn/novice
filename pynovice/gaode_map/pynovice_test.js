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
 <div class="info" id="text">
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
    var lineArr = [[116.478935,39.997761],[116.478939,39.997825],[116.478912,39.998549],[116.478912,39.998549],[116.478998,39.998555],[116.478998,39.998555],[116.479282,39.99856],[116.479658,39.998528],[116.480151,39.998453],[116.480784,39.998302],[116.480784,39.998302],[116.481149,39.998184],[116.481573,39.997997],[116.481863,39.997846],[116.482072,39.997718],[116.482362,39.997718],[116.483633,39.998935],[116.48367,39.998968],[116.484648,39.999861]];
    var cur_interval=[5,lineArr.length-10,lineArr.length-1];
</script>
  <script>
  	var stroke = eval(document.getElementById("stroke").value);
    var lineArr_main=lineArr.slice(cur_interval[stroke[0]],cur_interval[stroke.slice(-1)]);

    var map = new AMap.Map("container", {
        resizeEnable: true,
        center: [116.397428, 39.90923],
        zoom: 17
    });
    function showInfoClick(e){
        var text = '鼠标点击位置：[ '+e.lnglat.getLng()+','+e.lnglat.getLat()+' ]'
        document.querySelector("#text").innerText = text;
    }
    map.on('click', showInfoClick);

    marker = new AMap.Marker({
                map: map,
                position: lineArr_main[0],
                icon: "https://webapi.amap.com/images/car.png",
                offset: new AMap.Pixel(-26, -13),
                autoRotation: true,
                angle:-90
            });

    var polyline1 = new AMap.Polyline({
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
        path: lineArr_main,
        showDir:true,
        strokeColor: "#28F",  //线颜色
        strokeOpacity: 1,     //线透明度
        strokeWeight: 6,      //线宽
        // strokeStyle: "solid"  //线样式
    });

    var passedPolyline = new AMap.Polyline({
        map: map,
        // path: lineArr,
        strokeColor: "#AF5",  //线颜色
        //strokeOpacity: 1,     //线透明度
        strokeWeight: 6,      //线宽
        // strokeStyle: "solid"  //线样式
    });
    marker.on('moving', function (e) {
        passedPolyline.setPath(e.passedPath);
    });





    map.setFitView();
    function startAnimation () {
        var speed = document.getElementById("speed").value;
        marker.moveAlong(lineArr_main, speed );
    }
    function pauseAnimation () {
        marker.pauseMove();
    }
    function resumeAnimation () {
        marker.resumeMove();
    }
</script>
</body>
</html>