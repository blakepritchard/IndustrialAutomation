pkill uwsgi 
sudo rm /tmp/SatTrackerWeb.sock 

/usr/local/bin/uwsgi --ini ./SatTrackerPiWebsite/uwsgi_config.ini --uid www-data --gid www-data --daemonize ../sat_tracker_web_uwsgi.log

sudo chown www-data /tmp/SatTrackerWeb.sock
