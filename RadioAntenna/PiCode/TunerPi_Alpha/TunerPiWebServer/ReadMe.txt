
#( https://iotbytes.wordpress.com/python-flask-web-application-on-raspberry-pi-with-nginx-and-uwsgi/ )
https://stackoverflow.com/questions/31252791/flask-importerror-no-module-named-flask


# to configure nginx for website copy file: 
   sudo cp /home/pi/IndustrialAutomation/RadioAntenna/PiCode/TunerPi_Alpha/TunerPiWebServer/TunerWeb_proxy /etc/nginx/sites-available/


# create a symlink to enable nginx:
   sudo ln -s /etc/nginx/sites-available/TunerWeb_proxy /etc/nginx/sites-enabled/

# add website user to tty group:
    sudo adduser www-data tty

# create database:
cd /home/pi/IndustrialAutomation/RadioAntenna/PiCode/TunerPi_Alpha/TunerPiWebServer/
export FLASK_APP=TunerWeb.py 
export FLASK_ENV=development

sqlite3 app.db
.quit

sudo chmod 666 app.db
flask db upgrade

printenv FLASK_APP
flask run


# make www-data the owner of the subfolder:
    sudo chown www-data /home/pi/IndustrialAutomation/RadioAntenna/PiCode/TunerPi_Alpha/TunerPiWebServer


# ( https://blog.eq8.eu/til/raspberi-pi-as-kiosk-load-browser-on-startup-fullscreen.html )
# to configure chromium to start in the GUI copy the following text into ~/.config/lxsession/LXDE-pi/autostart
   @chromium-browser --kiosk http://tuner-pi


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
#As root, Create Symbolic Link to  the following files into /etc/systemd/system:
sudo ln -s /home/pi/IndustrialAutomation/RadioAntenna/PiCode/TunerPi_Alpha/TunerPiDaemon/tuner_pi_daemon.service /etc/systemd/system
sudo ln -s /home/pi/IndustrialAutomation/RadioAntenna/PiCode/TunerPi_Alpha/TunerPiWebServer/tuner_pi_web_server.service /etc/systemd/system 
sudo ln -s /home/pi/IndustrialAutomation/RadioAntenna/PiCode/TunerPi_Alpha/TunerPiWebClient/tuner_pi_web_client.service /etc/systemd/system 


#enable services to start at boot:
sudo systemctl enable tuner_pi_daemon.service 
sudo systemctl enable tuner_pi_web_server.service
sudo systemctl enable tuner_pi_web_client.service 


# test the scripts by starting them manually:
   sudo systemctl start tuner_pi_daemon.service  

# view the logs with the systemctl status command:
   sudo systemctl status tuner_pi_daemon.service  



