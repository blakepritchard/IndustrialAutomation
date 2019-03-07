
#( https://iotbytes.wordpress.com/python-flask-web-application-on-raspberry-pi-with-nginx-and-uwsgi/ )


# make www-data the owner of the subfolder:
    sudo chown www-data /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite

# to configure nginx for website copy file: 
   cp /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/SatTrackerWeb_proxy /etc/nginx/sites-available/


# create a symlink to enable nginx:
   sudo ln -s /etc/nginx/sites-available/SatTrackerWeb_proxy /etc/nginx/sites-enabled/

# add website user to tty group:
    sudo adduser www-data tty


# ( https://blog.eq8.eu/til/raspberi-pi-as-kiosk-load-browser-on-startup-fullscreen.html )
# to configure chromium to start in the GUI copy the following text into ~/.config/lxsession/LXDE-pi/autostart
   @chromium-browser --kiosk http://sat-tracker-pi


###############################################################################################################################################################
# Deprecated:
#  to configure the Pi to run the website automatically add the following text to: /etc/rc.local
#
#    cd /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/
#    rm ./SatTrackerPiWebsite/sat_tracker_web_uwsgi.log
#    bash start_tracker.bash > start_tracker.log &
#    /usr/local/bin/uwsgi --ini ./SatTrackerPiWebsite/uwsgi_config.ini --uid www-data --gid www-data --daemonize ./SatTrackerPiWebsite/sat_tracker_web_uwsgi.log
#################################################################################################################################################################


# ( https://www.raspberrypi.org/documentation/linux/usage/systemd.md )



#On Raspian Use systemd to start the WebServer, TrackerDaemon, and WebClient.
#As root, Copy the following files into /etc/systemd/system:
  sudo cp /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/sat_tracker_pi_daemon.service /etc/systemd/system


# test the scripts by starting them manually:
   sudo systemctl start sat_tracker_pi_daemon.service  

