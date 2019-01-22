$( document ).ready(function() {
    setInterval(function() {
        update_rotor_status()
      }, 5000);
});

function update_rotor_status(){
    req_status = $.get("/sat_tracker/api/rotator/status", function(data){update_dashboard(data)});
    req_status = $.get("/sat_tracker/api/rotator/log", function(data){update_logview(data)});
}

function update_dashboard(data){
    rotator_status = JSON.parse(data)
    $("#azimuth_current").text(rotator_status.azimuth_degrees);
    $("#elevation_current").text(rotator_status.elevation_degrees);
    $("#polarity_current").text(rotator_status.polarity_degrees);
}
function update_logview(data){
    log_records = JSON.parse(data);

    $( "logview" ).html(data);
}