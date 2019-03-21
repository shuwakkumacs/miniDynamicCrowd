// set figure environment
var height = "100px";
var funcWidthPerc = "80%";
var topOffset = "20px";
var bottomOffset = "25px";
var leftOffset = "60px";
var rightOffset = "30px";
var padding = "10px";

// initialize graph area
$("#plugin-wrapper").css("height",height);
$("#function-wrapper").css({
    top: topOffset,
    left: leftOffset,
    width: `calc(${funcWidthPerc} - ${leftOffset} - ${rightOffset})`,
    height: `calc(100% - ${bottomOffset} - ${topOffset})`
});
$("#right-boxes").css({
    "left": `calc(${funcWidthPerc} + ${padding})`,
    "top": padding,
    "width": `calc(calc(100% - ${funcWidthPerc}) - calc(${padding} * 2))`,
    "height": `calc(100% - calc(${padding} * 2))`,
});
$("#xticks-svg").css({
    "top": 0,
    "left": "-"+leftOffset,
    "height": "100%",
    "width": `calc(${leftOffset} - 3px)`
});
$("#yticks-svg").css({
    "top": "calc(100% + 3px)",
    "left": 0,
    "height": `calc(${bottomOffset} - 3px)`,
    "width": "100%"
});
$("#zeroticks-svg").css({
    "top": "calc(100% + 3px)",
    "left": "-"+leftOffset,
    "height": bottomOffset,
    "width": leftOffset
});

// draw graph
var X = [0,    1,    2,    3,    4,   60];
var Y = [0, 0.01, 0.02, 0.03, 0.04, 0.05];
var XPerc = X.map(function(item) { return item/Math.max(...X)*100 });
var YPerc = Y.map(function(item) { return (100-item/Math.max(...Y)*80) });
var Xmax = X[X.length-1];

drawSteps(X,Y,{},$("#function-group"));
drawProgressAll({},$("#progressbar-group"));
drawAxes({},$("#axes-group"));

// draw ticks
var idxPeakBegin = YPerc.indexOf(20)-1;
var xPeakBegin = X[idxPeakBegin];
var xPeakEnd = X[idxPeakBegin+1];
var xPercBegin = XPerc[idxPeakBegin];
var xPercEnd = XPerc[idxPeakBegin+1];
var xPeakBeginStr = secToMinStr(xPeakBegin);
var xPeakEndStr = secToMinStr(xPeakEnd);
appendElem("text", {id: "xTicksPeakBegin", x: xPercBegin+"%", y: 0, "text-anchor": "middle", "dominant-baseline": "hanging"}, $("#yticks-svg"), xPeakBeginStr);
if(xPeakEnd!=Xmax)
    appendElem("text", {id: "xTicksPeakEnd", x: xPercEnd+"%", y: 0, "text-anchor": "middle", "dominant-baseline": "hanging"}, $("#yticks-svg"), xPeakEndStr);
$("#yTicksPeak").text("$"+Y[idxPeakBegin+1]);
$("#xTicksLimit").text(secToMinStr(Xmax));

// define animation
var keyframesX = [];
for(var i=0; i<Xmax; i++){
    keyframesX.push({
        "name": "progressX-"+i,
        "0%": { transform: `translateX(${100*i/Xmax}%)` },
        "100%": { transform: `translateX(${100*(i+1)/Xmax}%)` }
    });
}
$.keyframe.define(keyframesX);

// animate
var setNextAnimation = function(){
    var now = new Date().getTime();
    var lag = now - (baseTS + secElapsed*1000);
    var duration = (1000 - lag)/1000;
    $("#progressbar-group").css({
        "animation": `progressX-${secElapsed} ${duration}s linear`,
        "animation-fill-mode": "forwards"
    });
    $("#progressBarPlot").css("transform",`translateY(${YPerc[kfi+1]}%)`);
    $("#elapsed-time").text("Time  "+secToMinStr(secElapsed));
    $("#reward").text("$"+Y[kfi+1]);
    if(X[kfi]==secElapsed && secElapsed) {
        $("#right-boxes").addClass("flash-animation");
    }
    if(X[kfi+1]==secElapsed+1) {
        kfi++;
    }
    secElapsed++;
};

var kfi = 0;
var secElapsed = 0;
var baseTS = new Date().getTime();
var amtHITAcceptedTime = getHITAcceptedTime();
console.log("baseTS-amtHITAcceptedTime");
console.log(baseTS-amtHITAcceptedTime);
setNextAnimation();
$("#progressbar-group").on("animationend",function(){
    if(secElapsed==Xmax) $(this).off("animationend");
    else setNextAnimation();
});
$("#right-boxes").on("animationend",function(){
    $("#right-boxes").removeClass("flash-animation");
});

//$("#reward").each(function(){
//    var height = $(this).height();
//    $(this).css("line-height",height+"px");
//});
//$("#elapsed-time").each(function(){
//    var height = $(this).height();
//    $(this).css("line-height",height+"px");
//});
