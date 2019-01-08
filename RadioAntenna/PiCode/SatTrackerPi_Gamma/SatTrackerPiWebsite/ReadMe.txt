
https://iotbytes.wordpress.com/python-flask-web-application-on-raspberry-pi-with-nginx-and-uwsgi/


to configure nginx for website copy file: 
/home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/SatTrackerWeb_proxy to /etc/nginx/sites-available




to configure the Pi to run the website automatically add the following text to: /etc/rc.local


/usr/local/bin/uwsgi --ini /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/uwsgi_config.ini --uid www-data --gid www-data --daemonize /var/log/uwsgi.log