<div class="info" id="text">
    鼠标点击位置：[lng_mars,lat_mars]
</div>
<script>
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

    function showInfoClick(e){
        var text = '鼠标点击位置：[ '+e.lnglat.getLng()+','+e.lnglat.getLat()+' ]'
        document.querySelector("#text").innerText = text;
    }
    map.on('mousemove', showInfoMove);
</script>