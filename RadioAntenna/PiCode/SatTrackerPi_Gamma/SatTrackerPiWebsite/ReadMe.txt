
to configure the Pi to run the website automatically add the following text to: /etc/rc.local


/usr/local/bin/uwsgi --ini /home/pi/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/uwsgi_config.ini --uid www-data --gid www-data --daemonize /var/log/uwsgi.log