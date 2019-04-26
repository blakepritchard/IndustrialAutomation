
intervalDisplay = false;
intervalTrackPolarity = false;
buttonTrackPolarity = false;


$( document ).ready(function() {
    $("#polarity_speed").val("1");
    $('#btnSetAzimuth').on("click" = function(){azimuth_set();});
    $('#btnSetElevation').on("click" = function(){elevation_set();});
    $('#btnSetPolarity').on("click" = function(){polarity_set();});
    $('#btnPolarityTrackingStart').on("click" = function(){polarity_tracking_update(1);});
    $('#btnPolarityTrackingStop').on("click" = function(){polarity_tracking_update(0);});
    screen_update_toggle();
});

function screen_update_toggle(){
    if(!intervalDisplay){
        intervalDisplay = setInterval(function() { update_rotor_status()}, 2000);
        $("#btnUpdateScreen").innerHTML = "Stop Screen Updates ";
    }
    else{ 
        clearInterval(intervalDisplay);
        intervalDisplay = false;
        $("#btnUpdateScreen").innerHTML = "Start Updating Screen";
    }
}

function update_rotor_status(){
    req_status = $.get("/sat_tracker/api/rotator/status", function(data){update_dashboard(data)});
    req_log = $.get("/sat_tracker/api/rotator/log", function(data){update_logview(data)});    
}



function polarity_tracking_update(is_tracking)
{
    command = ""
    if (is_tracking) {
        $("#btnSetPolarity").prop("disabled",true);
        $("#polarity_next").prop("disabled",true);       
        command = "PT"
    }
    else{
        $("#btnSetPolarity").prop("disabled",false);
        $("#polarity_next").prop("disabled",false);
        command = "SP"
        int_polarity_speed = 0        
    }

    int_polarity_current = Number($("#polarity_current").text())
    int_polarity_speed = Number($("#polarity_speed").val());

    var date = new Date();
    obj_polarity_command = {rotator_id: 1, command_code:command, command_value:int_polarity_speed };
    func_success = function(data){ $("#polarity_current").text(data.polarity_degrees); }
    post_rotator_command(obj_polarity_command, func_success)
}
 /*
    json_polarity_command = JSON.stringify(obj_polarity_command);
    resp_polarity_command = jQuery.ajax ({
        url: "/sat_tracker/api/rotator/command",
        type: "POST",
        data: json_polarity_command,
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function(data){
            $("#polarity_current").text(data.polarity_degrees);
        }
    });
*/



/*
function polarity_set(int_polarity_next){
    int_polarity_next = $("#polarity_next").val()
    obj_polarity_command = {rotator_id: 1, command_code:"PP", command_value:int_polarity_next };
    json_polarity_command = JSON.stringify(obj_polarity_command);
    resp_polarity_next = jQuery.ajax ({
        url: "/sat_tracker/api/rotator/command",
        type: "POST",
        data: json_polarity_command,
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function(data){
            $("#polarity_current").text(data.polarity_degrees);
            
        }
    });
} 
*/

function polarity_set(int_polarity_next){
    int_polarity_next = $("#polarity_next").val()
    obj_polarity_command = {rotator_id: 1, command_code:"PP", command_value:int_polarity_next };
    func_success = function(data){$("#polarity_current").text(data.polarity_degrees);}
    post_rotator_command(obj_polarity_command, func_success);
} 
function azimuth_set(int_azimuth_next){
    int_azimuth_next = $("#azimuth_next").val()
    obj_azimuth_command = {rotator_id: 1, command_code:"AZ", command_value:int_azimuth_next };
    func_success = function(data){$("#azimuth_current").text(data.azimuth_degrees);}
    post_rotator_command(obj_azimuth_command, func_success);
} 
function elevation_set(int_elevation_next){
    int_elevation_next = $("#elevation_next").val()
    obj_elevation_command = {rotator_id: 1, command_code:"EL", command_value:int_elevation_next };
    func_success = function(data){$("#elevation_current").text(data.elevation_degrees);}
    post_rotator_command(obj_elevation_command, func_success);
} 


function post_rotator_command(obj_rotator_command, func_success){
    json_rotator_command = JSON.stringify(obj_rotator_command);
    resp_rotator_next = jQuery.ajax ({
        url: "/sat_tracker/api/rotator/command",
        type: "POST",
        data: json_rotator_command,
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function(data){
            $("#polarity_current").text(data.polarity_degrees);
            
        }
    });    
}


function update_dashboard(data){
    $("#azimuth_current").text(data.azimuth_degrees);
    $("#elevation_current").text(data.elevation_degrees);
    $("#polarity_current").text(data.polarity_degrees);
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
