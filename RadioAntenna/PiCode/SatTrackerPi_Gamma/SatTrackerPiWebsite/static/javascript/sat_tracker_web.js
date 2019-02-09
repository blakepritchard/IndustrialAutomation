
intervalDisplay = false;
intervalTrackPolarity = false;
buttonTrackPolarity = false;
intPolarityCurrent = 0;


$( document ).ready(function() {
    intervalDisplay = setInterval(function() { update_rotor_status()}, 5000);
    buttonTrackPolarity = document.getElementById('btnTrackPolarity');   
    intPolarityCurrent = 0;
});

function update_rotor_status(){
    req_status = $.get("/sat_tracker/api/rotator/status", function(data){update_dashboard(data)});
    req_log = $.get("/sat_tracker/api/rotator/log", function(data){update_logview(data)});
}

function update_dashboard(data){
    rotator_status = JSON.parse(data)
    $("#azimuth_current").text(rotator_status.azimuth_degrees);
    $("#elevation_current").text(rotator_status.elevation_degrees);
    $("#polarity_current").text(rotator_status.polarity_degrees);
}
function update_logview(data){
    log_records = JSON.parse(data);
    log_html = "";
    for (var i = 0; i < log_records.length; i++)
    {
        log_message = log_records[i]

        if (-1 != log_message.search("FATAL")){
            log_html += "<font color='red'>"} 
        else if (-1 !=log_message.search("CRITICAL")){
            log_html += "<font color='orange'>"}
        else if (-1 !=log_message.search("WARNING")){
                log_html += "<font color='yellow'>"}   
        else{
            log_html += "<font color='green'>"
        }
        log_html += log_message +"</font><br> \n";
    }
    $("#logview").html(log_html);
}



function polarity_tracking_toggle(){
    if(!intervalTrackPolarity){
        req_status = $.get("/sat_tracker/api/rotator/status", function(data){polarity_tracking_start(data)});
    }
    else{ 
        clearInterval(intervalTrackPolarity);
        intervalTrackPolarity = false;
        buttonTrackPolarity.innerHTML = "Start Tracking";
    }
}

function polarity_tracking_start(data)
{
    rotator_status = JSON.parse(data);
    intPolarityCurrent = rotator_status.polarity_degrees;
    intervalTrackPolarity = setInterval(polarity_tracking_update,2000);
    buttonTrackPolarity.innerHTML = "Stop Tracking";

}

function polarity_tracking_update()
{
    int_polarity_current = Number($("#polarity_current").text())
    int_polarity_next = int_polarity_current + .5;
    polarity_move(int_polarity_next)

}

function polarity_set(int_polarity_next){
    int_polarity_next = $("#polarity_next").val()
    polarity_move(int_polarity_next)
}


function polarity_move(int_polarity_next){
    obj_polarity_next = {polarity_new: int_polarity_next};
    json_polarity_next = JSON.stringify(obj_polarity_next);
    resp_polarity_next = jQuery.ajax ({
        url: "/sat_tracker/api/rotator/polarity",
        type: "POST",
        data: json_polarity_next,
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function(data){
            $("#polarity_current").text(data.polarity_degrees);
            
        }
    });
} 
