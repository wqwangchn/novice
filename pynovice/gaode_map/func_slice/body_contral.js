
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
        行程： <input type="text" value="[0,1]" id="stroke">
    </div>
    <div class="input-item">
        <input type="submit" class="btn" value="开始动画" id="resume" onclick="startAnimation()"/>
        <input type="button" class="btn" value="停止动画" id="stroke" onclick="pauseAnimation()"/>
        <input type="button" class="btn" value="继续动画" id="resume" onclick="resumeAnimation()"/>
    </div>
</div>

function startAnimation () {
	var speed = document.getElementById("speed").value;
    marker.moveAlong(lineArr_main, speed );
}
function stopAnimation () {
    marker.stopMove();
}
