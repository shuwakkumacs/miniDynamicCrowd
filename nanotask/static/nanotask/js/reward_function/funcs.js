var appendElem = function(type, attr, $selector, content){
    var newLine = document.createElementNS('http://www.w3.org/2000/svg',type);
    for(var key in attr) {
        //if(key=="other"){
        //    var others = attr[key];
        //    if("content" in others
        newLine.setAttribute(key,attr[key]);
    }
    newLine.textContent = content;
    $selector.append(newLine);
};

var coordToPerc = function(x, y, xLim, yLim){
    xPerc = (x/xLim)*100;
    yPerc = 100-(y/yLim)*100;
    return [xPerc+"%", yPerc+"%"];
};

var calcPerc = function(a, b, operation){
    var aVal = parseFloat(a.substr(0,a.length-1))
    var bVal = parseFloat(b.substr(0,b.length-1))
    var ansVal = null;
    if(operation=="+") ansVal = aVal+bVal;
    else if(operation=="-") ansVal = aVal-bVal;
    else if(operation=="*") ansVal = aVal*bVal;
    else if(operation=="/") ansVal = aVal/bVal;
    return ansVal+"%";
};

var drawAxes = function(attr, $selector){
    var line1 = { 'x1': "0", 'y1': "100%", 'x2': "0", 'y2': "0",
                  'stroke-width': "4px", 'stroke': "black" };
    var line2 = { 'x1': "0", 'y1': "100%", 'x2': "100%", 'y2': "100%",
                  'stroke-width': "4px", 'stroke': "black" };
    appendElem("line", line1, $selector)
    appendElem("line", line2, $selector)
}

var drawProgressBar = function(attr, $selector){
    var line = { 'id': "progressBar", 'x1': "0", 'y1': "100%", 'x2': "0", 'y2': "0", 'stroke-width': "4px", 'stroke': "red" };
    for(var key in attr) line[key] = attr[key];
    appendElem("line", line, $selector)
};

var drawIntersectionPoint = function(attr, $selector){
    var circle = { 'id': "progressBarPlot", 'cx': "0", 'cy': "0", 'r': "6px", 'fill': "red" };
    for(var key in attr) circle[key] = attr[key];
    appendElem("circle", circle, $selector)
};

var drawProgressAll = function(attr, $selector){
    drawProgressBar(attr,$selector);
    drawIntersectionPoint(attr,$selector);
};

var drawSteps = function(X, Y, attr, $selector){
    var stroke_color = "#ff8100";
    var stroke_width = "2px";

    var stack = true;
    var fill_color = "#ff8100";
    var fill_color_peak = "#ff0000";
    var fill_opacity = "0.5";

    var xLim = Math.max(...X);
    var yLim = Math.max(...Y);

    var drawStep = function(x1,y1,x2,y2){
        var start = coordToPerc(x1, y1, xLim, yLim);
        var end = coordToPerc(x2, y2, xLim, yLim);

        var line1 = { 'x1': start[0], 'y1': start[1], 'x2': start[0], 'y2': end[1], 'stroke-width': stroke_width, 'stroke': stroke_color };
        var line2 = { 'x1': start[0], 'y1': end[1], 'x2': end[0], 'y2': end[1], 'stroke-width': stroke_width, 'stroke': stroke_color };
        appendElem("line", line1, $selector)
        appendElem("line", line2, $selector)

        if(stack){
            var rect = { 'x': start[0], 'y': end[1], 'width': calcPerc(end[0],start[0],"-"), 'height': calcPerc("100%",end[1],"-")}
            //if(end[1]=="0%")
            //    rect["style"] = `fill:${fill_color_peak};opacity:${fill_opacity};stroke-width:3px;stroke:red;stroke-opacity:0.5;`;
            //else
                rect["style"] = `fill:${fill_color};opacity:${fill_opacity};`;
            appendElem("rect", rect, $selector);
        }
    };

    for(var i=0; i<X.length-1; i++){ drawStep(X[i],Y[i],X[i+1],Y[i+1]); }
};

var secToMinStr = function(sec){
    var min = parseInt(sec/60);
    var secRest = parseInt(sec%60);
    return ("00"+min).slice(-2)+":"+("00"+secRest).slice(-2);
};

var getHITAcceptedTime = function(){
    var amtStringToDatetime = function(str){
        var splits1 = str.split("/");
        var splits2 = splits1[2].split(" ");
        var splits3 = splits2[1].split(":");
        var year = parseInt(splits2[0]);
        var month = parseInt(splits1[0])-1;
        var day = parseInt(splits1[1]);
        var hour = splits3[2].slice(2)=="am" ? parseInt(splits3[0]) : parseInt(splits3[0])+12;
        var minute = parseInt(splits3[1]);
        var second = parseInt(splits3[2].slice(0,-2));
        return new Date(year,month,day,hour,minute,second).getTime();
    };
    var $amtCompletionTimer = $($(document).xpathEvaluate('//*[contains(@data-react-class,"CompletionTimer")]')[0]);
    var expirationTime = $amtCompletionTimer.find(".completion-timer").attr("title");
    var completionInSeconds = JSON.parse($amtCompletionTimer.attr("data-react-props"))["originalTimeToCompleteInSeconds"];
    var amtHITExpirationTime = amtStringToDatetime(expirationTime);
    return amtHITExpirationTime-completionInSeconds*1000;
};


$.fn.xpathEvaluate = function (xpathExpression) {
    // NOTE: vars not declared local for debug purposes
    $this = this.first(); // Don't make me deal with multiples before coffee

    // Evaluate xpath and retrieve matching nodes
    xpathResult = this[0].evaluate(xpathExpression, this[0], null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);

    result = [];
    while (elem = xpathResult.iterateNext()) {
        result.push(elem);
    }

    $result = jQuery([]).pushStack( result );
    return $result;
}
