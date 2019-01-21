$( document ).ready(function() {
    setInterval(function() {
        update_rotor_status()
      }, 3000);
});

function update_rotor_status(){
    req = $.get("/api/rotator/status", function(data){
        update_dashboard(data)
    });
}

function update_dashboard(data){
    $("#azimuth_current").text(data.azimuth_degrees);
    $("#elevation_current").text(data.elevation_degrees);
    $("#polarity_current").text(data.polarity_degrees);
}