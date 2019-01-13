
https://iotbytes.wordpress.com/python-flask-web-application-on-raspberry-pi-with-nginx-and-uwsgi/


to configure nginx for website copy file: 
   cp /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/SatTrackerWeb_proxy /etc/nginx/sites-available/


create a symlink to enable nginx:
   sudo ln -s /etc/nginx/sites-available/SatTrackerWeb_proxy /etc/nginx/sites-enabled/

add website user to tty group:
    sudo adduser www-data tty

to configure the Pi to run the website automatically add the following text to: /etc/rc.local

    cd /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/
    bash start_tracker.bash > start_tracker.log &

    /usr/local/bin/uwsgi --ini ./SatTrackerPiWebsite/uwsgi_config.ini --uid www-data --gid www-data --daemonize /var/log/uwsgi.log
