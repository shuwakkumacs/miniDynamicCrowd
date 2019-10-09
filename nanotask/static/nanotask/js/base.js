var hrefSplit = window.location.href.split("/");
PROJECT_NAME = hrefSplit[hrefSplit.length-2];

MTURK_WORKER_ID = turkGetParam("workerId", "TEST_WORKER");
MTURK_ASSIGNMENT_ID = turkGetParam("assignmentId", "ASSIGNMENT_ID_NOT_AVAILABLE");
MTURK_HIT_ID = turkGetParam("hitId", "TEST_DUMMY_HIT");
MTURK_GROUP_ID = document.referrer.match(/https:\/\/worker(sandbox)?.mturk.com\/projects\//g) ? document.referrer.split("/")[4] : turkGetParam("groupId", "TEST_DUMMY_GROUP");

TEST_MODE = turkGetParam("production", false) ? false : true;
PREVIEW_MODE = MTURK_ASSIGNMENT_ID=="ASSIGNMENT_ID_NOT_AVAILABLE" ? true : false;
  
BASE_URL = window.location.origin+"/";

nanotasksPerHIT = -1;
submittedNanotasks = 0;
nanotaskStatus = "first";

timeNanotaskStarted = null;

var checkVisit = function(){
    var visited = false;
    var visitedId = MTURK_GROUP_ID+"-"+MTURK_WORKER_ID;
    var visitedIdsStr = sessionStorage.getItem("visitedIds");
    if(visitedIdsStr){
        visitedIds = visitedIdsStr.split(",");
        if(visitedIds.indexOf(visitedId) > -1) visited = true;
        if(!visited) {
            visitedIds.push(visitedId);
            sessionStorage.setItem("visitedIds", visitedIds);
        }
    } else {
       sessionStorage.setItem("visitedIds", visitedId);
    }
    return visited;
};
 
var randomSeed = function(){
    var l = 16;
    var c = "abcdefghijklmnopqrstuvwxyz0123456789";
    var cl = c.length;
    var r = "";
    for(var i=0; i<l; i++) r += c[Math.floor(Math.random()*cl)];
    return r;
};

function getNanotaskAnswers(that, success, error){
    var answersJSON = {};
    var errorNames = [];

    if($(that).attr("name")){

        var name = $(that).attr("name");
        var value = $(that).val();
        answersJSON[name] = value;

    }

    $answers = $(".nano-answer");
    all_inputs = {};
    $answers.each(function(i,ans){

        if(ans.tagName=="INPUT")
            var type = ans.type;
        else if(ans.tagName=="TEXTAREA")
            var type = "textarea";
        else if(ans.tagName=="SELECT")
            var type = "select";

        var name = ans.name;
        var required = $(ans).hasClass("nano-required");
        if(type in all_inputs) {
            if(all_inputs[type]["names"].indexOf(name)==-1) {
                all_inputs[type]["names"].push(name);
                all_inputs[type]["required"].push(required);
            }
        } else {
            all_inputs[type] = {};
            all_inputs[type]["names"] = [name];
            all_inputs[type]["required"] = [required];
        }

    });

    for(var type in all_inputs){
        for(var i in all_inputs[type]["names"]){

            var name = all_inputs[type]["names"][i];
            var required = all_inputs[type]["required"][i];

            switch(type){

                case "checkbox":
                    var $checked = $(`.nano-answer[type=checkbox][name=${name}]:checked`);
                    answersJSON[name] = [];
                    $checked.each(function(j,checked){
                        answersJSON[name].push($(checked).val());
                    });
                    if(required && answersJSON[name].length==0) errorNames.push(name);
                    break;

                case "radio":
                    var $checked = $(`.nano-answer[type=radio][name=${name}]:checked`);
                    answersJSON[name] = $checked.val();
                    if(required && typeof(answersJSON[name])==="undefined") errorNames.push(name);
                    break;

                case "select":
                    var $selected = $(`select.nano-answer[name=${name}] option:selected`);
                    answersJSON[name] = $selected.val();
                    if(required && typeof(answersJSON[name])==="undefined") errorNames.push(name);
                    break;

                default:
                    answersJSON[name] = $(`.nano-answer[name=${name}]`).val();
                    if(required && (typeof(answersJSON[name])==="undefined" || answersJSON[name]==="")) errorNames.push(name);
                    break;
            }
        }
    }

    if(errorNames.length) error(errorNames);
    else success(answersJSON);
}


var loadNanotask = function() {

    var afterNanotaskLoadHandler = function(nanotask){

        if(nanotask.msg){
            $("#base-nanotask").html(nanotask.html);
        }

        else if(!nanotask.info)
            afterNanotaskLoadErrorHandler();

        else if(nanotask.status=="finish" || submittedNanotasks>nanotasksPerHIT)
            submitHIT();

        else {
            if(nanotask.status=="last" && submittedNanotasks<nanotasksPerHIT)
                alert("Well done! There seem to be no more tasks available. Please give us an extra minute for a few survey questions. Thank you for your contribution!");
    
            nanotaskStatus = nanotask.status
            sessionStorage.setItem("nanotaskStatus", nanotaskStatus);

            if(["first","last"].indexOf(nanotaskStatus) > -1) {
                $("#base-submitted-num-box").hide();
                $("#nph-description").hide();
            } else {
                $("#base-submitted-num-box").show();
                $("#nph-description").show();
                $("#base-submitted-num-box>span.submitted-num").text(submittedNanotasks+1);
            }
            $("#base-nanotask").html(nanotask.html);
            $("#base-nanotask").fadeIn("normal");
            timeNanotaskStarted = new Date();
            var idsAllInputVal = $("#nano-ids-all").val();
            if(idsAllInputVal=="") idsAll = [];
            else idsAll = JSON.parse(idsAllInputVal);
    
            $(".nano-submit").on("click", function(){
                getNanotaskAnswers(this, function(answersJSON){
                    var secsElapsed = (new Date() - timeNanotaskStarted)/1000;
                    $("#base-nanotask").fadeOut("fast");
                    idsAll.push(nanotask.info.id);
                    $("#nano-ids-all").val(JSON.stringify(idsAll));

                    data = {
                        "id": nanotask.info.id,
                        "sec": secsElapsed,
                        "answer": answersJSON,
                        "project_name": PROJECT_NAME,
                        "status": nanotaskStatus
                    };
                    submitNanotask(data, function(){
                        if(["first", "last"].indexOf(nanotaskStatus) == -1) { submittedNanotasks += 1; }
                        if(nanotaskStatus=="first") nanotaskStatus = "";
                        sessionStorage.setItem("submittedNanotasks", submittedNanotasks);
                        sessionStorage.setItem("nanotaskStatus", nanotaskStatus);
                        if(nanotaskStatus=="last") submitHIT();
                        else loadNanotask();
                    }, function(){
                        alert("We're sorry, an error occured on sending data --- no worries, this HIT will be submitted now and you will be paid for this :) Thank you for your cooperation!");
    	            	submitHIT();
                    });
                }, function(errorNames){
                    var alertStr = "Please fill the required fields to submit this task:\n";
                    for(var i in errorNames){
                        var $elem = $(`*[name=${errorNames[i]}]`).eq(0);
                        var alt = $elem.attr("alt");
                        if(!alt) alt = $elem.attr("name");
                        alertStr += ` - ${alt}\n`;
                    }
                    alert(alertStr);
                    return false;
                });

            });
        }
    };
    
    var afterNanotaskLoadErrorHandler = function(a,b,c){
        if(submittedNanotasks==0){
            noTaskAlert();
        } else {
            noMoreTaskAlert(submitHIT);
        }
    };

    var sessionTabId = null;


    if(PREVIEW_MODE) {

        nanotaskStatus = "__preview__";
        $("#base-instruction-button").click();
        sessionTabId = "";
    }

    else {

        if(!checkVisit()) $("#base-instruction-button").click();

        nanotasksPerHIT = $("#nanotasks-per-hit").val();

        var sessionSubmittedNanotasks = sessionStorage.getItem("submittedNanotasks");
        submittedNanotasks = sessionSubmittedNanotasks ? parseInt(sessionSubmittedNanotasks): 0;

        nanotaskStatus = sessionStorage.getItem("nanotaskStatus");

        if(nanotaskStatus===null || typeof(nanotaskStatus)==="undefined" || nanotaskStatus==="undefined") nanotaskStatus = "first";

        if(!sessionStorage.tabID) {
            sessionTabId = randomSeed();
            sessionStorage.tabID = sessionTabId;
        } else {
            sessionTabId = sessionStorage.tabID;
        }

        if(typeof(nanotaskStatus)==="undefined") nanotaskStatus = "first";
        if(submittedNanotasks == nanotasksPerHIT) nanotaskStatus = "last";

        sessionStorage.setItem("nanotaskStatus", nanotaskStatus);

    }

    $.ajax({
        type: "POST",
        url: BASE_URL + "nanotask/nanotask/"+PROJECT_NAME+"/",
        data: JSON.stringify({
            "mturk_worker_id": MTURK_WORKER_ID,
            "session_tab_id": sessionTabId,
            "user_agent": window.navigator.userAgent,
            "status": nanotaskStatus
        }),
        success: afterNanotaskLoadHandler,
        error: afterNanotaskLoadErrorHandler
    });

};

var refreshPage = function(){
    sessionStorage.removeItem("submittedNanotasks");
    sessionStorage.setItem("nanotaskStatus", "first");
    if(TEST_MODE) { setTimeout(function(){ window.location.reload(); }, 500); }
    else $("#mturk_form").submit();
};

var submitHIT = function(){
    var data = {};
    data["mturk_assignment_id"] = MTURK_ASSIGNMENT_ID;
    data["mturk_worker_id"] = MTURK_WORKER_ID;
    data["mturk_hit_id"] = MTURK_HIT_ID;
    data["project_name"] = PROJECT_NAME;
    data["ids"] = JSON.parse($("#nano-ids-all").val());
    $("#base-nanotask-submitted").show();
    $.ajax({
        type: "POST",
        url: BASE_URL + "nanotask/assignment/save/",
        data: JSON.stringify(data),
        success: refreshPage,
        error: function(){
            $("#mturk_form").submit();
        }
    });
};

var submitNanotask = function(data, success, error){
    data["mturk_worker_id"] = MTURK_WORKER_ID;
    $.ajax({
        type: "POST",
        url: BASE_URL + "nanotask/answer/save/",
        dataType: "json",
        data: JSON.stringify(data),
        success: success,
        error: error
    });
}

var noMoreTaskAlert = function(callback){
    alert("Well done! There are no more tasks available -- this HIT will be automatically submitted. We appreciate your help! :)");
    callback();
};

var noTaskAlert = function(){
    alert("We're sorry but there are currently no tasks available, so please return this HIT. :( Thank you for your cooperation!");
};


$("#base-instruction-button").on("click", function(){
    $("#base-instruction-shadow").fadeIn("normal");
    $("#base-instruction").animate({"marginTop":"+=200px", "display": "block"});
    $("#base-instruction").show();
    $(this).prop("disabled", true);
});
$("#base-instruction-shadow, #base-instruction-close-button").on("click", function(){
    $("#base-instruction").animate({"marginTop":"-=200px", "display": "none"});
    $("#base-instruction-shadow").fadeOut("normal");
    $("#base-instruction-button").prop("disabled", false);
});
$("#base-instruction").on("click", function(e){
    e.stopPropagation();
});
$("#dev-btn-start-nanotasks").on("click",function(){
    var workerId = $("#dev-worker-id").val();
    if(workerId!="") window.location.href = "./?assignmentId=test&workerId="+workerId;
});
$("#dev-btn-reset").on("click", refreshPage);

$(function(){
    if(TEST_MODE) $("#top-dev-bar").show();
    if(PREVIEW_MODE) {
        $("#top-dev-bar-inner-preview").show();
    } else {
        $("#top-dev-bar-inner").show();
    }
    loadNanotask();
});

