var hrefSplit = window.location.href.split("/");
PROJECT_NAME = hrefSplit[hrefSplit.length-2];

MTURK_WORKER_ID = turkGetParam("workerId", "TEST_WORKER");
MTURK_ASSIGNMENT_ID = turkGetParam("assignmentId", "ASSIGNMENT_ID_NOT_AVAILABLE");
MTURK_HIT_ID = turkGetParam("hitId", null);

TEST_MODE = MTURK_ASSIGNMENT_ID=="test" ? true : false;

//BASE_URL = "http://localhost/DynamicCrowd/";
BASE_URL = window.location.origin+"/";

nanotasksPerHIT = -1;
submittedNanotasks = 0;

//var getProject = function(success, error){
//    $.ajax({
//        type: "GET",
//        url: BASE_URL + "nanotask/project/"+PROJECT_NAME+"/",
//        success: success,
//        error: error
//    });
//};

var loadPreviewNanotask = function() {
    $.ajax({
        type: "GET",
        url: BASE_URL + "nanotask/nanotask/"+PROJECT_NAME+"/"+MTURK_WORKER_ID+"/preview/",
        success: function(nanotask){
            $("#base-nanotask-wrapper").html(nanotask.html);
        }
    });
};

var loadNanotask = function() {
    var afterNanotaskLoadHandler = function(nanotask){
        if(!nanotask.info) afterNanotaskLoadErrorHandler();
        $("#base-submitted-num-box>span.submitted-num").text(submittedNanotasks+1);
        $("#base-nanotask-wrapper").html(nanotask.html);
        $("#base-nanotask-wrapper").fadeIn("normal");
        var idsAllInputVal = $("#nano-ids-all").val();
        var answersAllInputVal = $("#nano-answers-all").val();
        if(idsAllInputVal=="") {
            idsAll = [];
            answersAll = [];
        } else {
            idsAll = JSON.parse(idsAllInputVal);
            answersAll = JSON.parse(answersAllInputVal);
        }
    
        $(".nano-submit").on("click", function(){
            $("#base-nanotask-wrapper").fadeOut("fast");
            var answersJSON = {};

            if($(this).attr("name")){
                var name = $(this).attr("name");
                var value = $(this).val();
                answersJSON[name] = value;
            } else {
                $answers = $(".nano-answer");
                for(var i in $answers){
                    var $answer = $answers.eq(i);
                    var name = $answer.attr("name");
                    var value = $answer.val();
                    answersJSON[name] = value;
                }
            }
            idsAll.push(nanotask.info.id);
            answersAll.push(answersJSON);
            $("#nano-ids-all").val(JSON.stringify(idsAll));
            $("#nano-answers-all").val(JSON.stringify(answersAll));
            submittedNanotasks += 1;

            if(submittedNanotasks >= nanotasksPerHIT) submitHIT();
            else loadNanotask(nanotask.info.project_name);
        });
    };
    
    var afterNanotaskLoadErrorHandler = function(){
        if(submittedNanotasks==0){
            noTaskAlert();
        } else {
            noMoreTaskAlert(submitHIT);
        }
    };

    $.ajax({
        type: "GET",
        url: BASE_URL + "nanotask/nanotask/"+PROJECT_NAME+"/"+MTURK_WORKER_ID+"/",
        success: afterNanotaskLoadHandler,
        error: afterNanotaskLoadErrorHandler
    });

};

var submitHIT = function(){
    $("#base-nanotask-wrapper").html('<p style="width:100%;margin-top:100px;text-align:center;font-size:1.5em;">Submitting HIT...</p>');
    $.ajax({
        type: "POST",
        url: BASE_URL + "nanotask/answers/save/"+MTURK_WORKER_ID+"/",
        dataType: "json",
        data: JSON.stringify({
            "ids": JSON.parse($("#nano-ids-all").val()),
            "answers": JSON.parse($("#nano-answers-all").val())
        }),
        success: function(){
            if(TEST_MODE) { setTimeout(function(){ window.location.reload(); }, 500); }
            else $("#mturk_form").submit();
        },
        error: function(){
            console.log("submit hit error");
        }
    });
};

var noMoreTaskAlert = function(callback){
    alert("Well done! There are no more tasks available -- this HIT will be automatically submitted. Thank you for your help! :)");
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
$("#base-instruction-shadow").on("click", function(){
    $("#base-instruction").animate({"marginTop":"-=200px", "display": "none"});
    $(this).fadeOut("normal");
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
        loadNanotask();
    }
});

