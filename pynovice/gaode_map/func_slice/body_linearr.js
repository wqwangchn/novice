<script>
    var lineArr = [[116.478935,39.997761],[116.478939,39.997825],[116.478912,39.998549],[116.478912,39.998549],[116.478998,39.998555],[116.478998,39.998555],[116.479282,39.99856],[116.479658,39.998528],[116.480151,39.998453],[116.480784,39.998302],[116.480784,39.998302],[116.481149,39.998184],[116.481573,39.997997],[116.481863,39.997846],[116.482072,39.997718],[116.482362,39.997718],[116.483633,39.998935],[116.48367,39.998968],[116.484648,39.999861]];
    var cur_interval=[0,lineArr.length];
    var lineArr_main=lineArr.slice(cur_interval[0],cur_interval[1]);

    marker = new AMap.Marker({
                map: map,
                position: lineArr_main[0],
                icon: "https://webapi.amap.com/images/car.png",
                offset: new AMap.Pixel(-26, -13),
                autoRotation: true,
                angle:-90
            });

    // 绘制轨迹
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
<\script>