
intervalDisplay = false;
intervalTrackPolarity = false;
buttonTrackPolarity = false;


$( document ).ready(function() {
    intervalDisplay = setInterval(function() { update_rotor_status()}, 5000);
    buttonTrackPolarity = document.getElementById('btnTrackPolarity');   

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
        log_html += log_records[i] +"<br> \n";
    }
    $("#logview").html(log_html);
}

function toggleTrackingPolarity(){
    if(!intervalTrackPolarity){
        intervalTrackPolarity = setInterval(count,1000);
        buttonTrackPolarity.value = "Stop count!";
    }
    else{ 
        clearInterval(intervalTrackPolarity);
        intervalTrackPolarity = false;
        buttonTrackPolarity.value = "Start count!";
    }
}