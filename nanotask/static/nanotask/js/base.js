var hrefSplit = window.location.href.split("/");
PROJECT_NAME = hrefSplit[hrefSplit.length-2];

MTURK_WORKER_ID = turkGetParam("workerId", "TEST_WORKER");
MTURK_ASSIGNMENT_ID = turkGetParam("assignmentId", "ASSIGNMENT_ID_NOT_AVAILABLE");
MTURK_HIT_ID = turkGetParam("hitId", "TEST_DUMMY_HIT");

TEST_MODE = MTURK_ASSIGNMENT_ID=="test" ? true : false;

BASE_URL = window.location.origin+"/";

nanotasksPerHIT = -1;
submittedNanotasks = 0;
nanotaskStatus = "first";

timeNanotaskStarted = null;

var randomSeed = function(){
    var l = 16;
    var c = "abcdefghijklmnopqrstuvwxyz0123456789";
    var cl = c.length;
    var r = "";
    for(var i=0; i<l; i++) r += c[Math.floor(Math.random()*cl)];
    return r;
};

var loadPreviewNanotask = function() {
    $.ajax({
        type: "GET",
        url: BASE_URL + "nanotask/nanotask/"+PROJECT_NAME+"/?preview=1",
        success: function(nanotask){
            $("#base-nanotask").html(nanotask.html);
        }
    });
};

var loadNanotask = function() {
    var afterNanotaskLoadHandler = function(nanotask){
        if(nanotask.status=="finish" || submittedNanotasks>nanotasksPerHIT) submitHIT();
        else if(!nanotask.info) afterNanotaskLoadErrorHandler();
        else {
            nanotaskStatus = nanotask.status
            sessionStorage.setItem("nanotaskStatus", nanotaskStatus);

            $("#base-submitted-num-box").hide();
            if(nanotaskStatus=="first") {
                //$("#base-submitted-num-box-first").show();
            }
            else if(nanotaskStatus=="last") {
                //$("#base-submitted-num-box-last").show();
            }
            else {
                $("#base-submitted-num-box").show();
                $("#base-submitted-num-box>span.submitted-num").text(submittedNanotasks+1);
            }
            $("#base-nanotask").html(nanotask.html);
            $("#base-nanotask").fadeIn("normal");
            timeNanotaskStarted = new Date();
            var idsAllInputVal = $("#nano-ids-all").val();
            if(idsAllInputVal=="") idsAll = [];
            else idsAll = JSON.parse(idsAllInputVal);
    
            $(".nano-submit").on("click", function(){
                var secsElapsed = (new Date() - timeNanotaskStarted)/1000;
                $("#base-nanotask").fadeOut("fast");
                var answersJSON = {};

                if($(this).attr("name")){

                    var name = $(this).attr("name");
                    var value = $(this).val();
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

                    if(ans.type in all_inputs) {
                        if(all_inputs[ans.type].indexOf(ans.name)==-1)
                            all_inputs[ans.type].push(ans.name);
                    } else {
                        all_inputs[ans.type] = [ans.name];
                    }

                });

                for(var type in all_inputs){
                    for(var i in all_inputs[type]){

                        var name = all_inputs[type][i];

                        switch(type){

                            case "checkbox":
                                var $checked = $(`.nano-answer[type=checkbox][name=${name}]:checked`);
                                answersJSON[name] = [];
                                $checked.each(function(j,checked){
                                    answersJSON[name].push($(checked).val());
                                });
                                break;

                            case "radio":
                                var $checked = $(`.nano-answer[type=radio][name=${name}]:checked`);
                                answersJSON[name] = $checked.val();
                                break;

                            case "select":
                                var $selected = $(`.nano-answer[type=select][name=${name}] option:selected`);
                                answersJSON[name] = $selected.val();
                                break;

                            default:
                                answersJSON[name] = $(`.nano-answer[name=${name}]`).val();
                                break;
                        }
                    }
                }

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
                    if(["first","last"].indexOf(nanotaskStatus) == -1) { submittedNanotasks += 1; }
                    if(nanotaskStatus=="first") nanotaskStatus = "";
                    sessionStorage.setItem("submittedNanotasks", submittedNanotasks);
                    if(nanotaskStatus=="last") submitHIT();
                    else loadNanotask();
                }, function(){
                    alert("We're sorry, an error occured on sending data --- no worries, this HIT will be submitted now and you will be paid for this :) Thank you for your cooperation!");
    	        	submitHIT();
                });
            });
        }
    };
    
    var afterNanotaskLoadErrorHandler = function(){
        if(submittedNanotasks==0){
            noTaskAlert();
        } else {
            noMoreTaskAlert(submitHIT);
        }
    };


    if(typeof(nanotaskStatus)==="undefined") nanotaskStatus = "first";
    if(submittedNanotasks == nanotasksPerHIT) nanotaskStatus = "last";

    sessionStorage.setItem("nanotaskStatus", nanotaskStatus);


    $.ajax({
        type: "POST",
        url: BASE_URL + "nanotask/nanotask/"+PROJECT_NAME+"/",
        data: JSON.stringify({
            "mturk_worker_id": MTURK_WORKER_ID,
            "session_tab_id": sessionStorage.tabID,
            "user_agent": window.navigator.userAgent,
            "status": nanotaskStatus
        }),
        success: afterNanotaskLoadHandler,
        error: afterNanotaskLoadErrorHandler
    });
};

var submitHIT = function(){
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
        success: function(){
            sessionStorage.removeItem("submittedNanotasks");
            sessionStorage.setItem("nanotaskStatus", "first");
            if(TEST_MODE) { setTimeout(function(){ window.location.reload(); }, 500); }
            else $("#mturk_form").submit();
        },
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
    alert("We're sorry but there are currently no tasks available :( Please try again later. Thank you!");
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


$(function(){
    nanotasksPerHIT = $("#nanotasks-per-hit").val();
    if(MTURK_ASSIGNMENT_ID=="ASSIGNMENT_ID_NOT_AVAILABLE") {
        loadPreviewNanotask();
        $("#base-instruction-button").click();
    } else { 
        $("#base-submitted-num-box").show();

        var sessionSubmittedNanotasks = sessionStorage.getItem("submittedNanotasks");
        submittedNanotasks = sessionSubmittedNanotasks ? parseInt(sessionSubmittedNanotasks): 0;

        nanotaskStatus = sessionStorage.getItem("nanotaskStatus");
        if(nanotaskStatus===null) nanotaskStatus = "first";

        if(!sessionStorage.tabID) sessionStorage.tabID = randomSeed();

        loadNanotask();
    }
});

