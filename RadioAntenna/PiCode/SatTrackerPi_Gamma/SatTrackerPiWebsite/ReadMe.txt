
https://iotbytes.wordpress.com/python-flask-web-application-on-raspberry-pi-with-nginx-and-uwsgi/


to configure nginx for website copy file: 
   cp /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/SatTrackerWeb_proxy /etc/nginx/sites-available/


create a symlink to enable nginx:
   sudo ln -s /etc/nginx/sites-available/SatTrackerWeb_proxy /etc/nginx/sites-enabled/


to configure the Pi to run the website automatically add the following text to: /etc/rc.local

cd /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/
bash start_tracker.bash > /home/pi/logs/SatTrackerPi/satTrackerPi.log &
/usr/local/bin/uwsgi --ini /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/uwsgi_config.ini --uid www-data --gid www-data --daemonize /var/log/uwsgi.log
