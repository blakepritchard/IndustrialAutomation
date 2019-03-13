sudo chown pi SatTrackerPiWebServer/
git fetch --all
git reset --hard origin/master
git pull
sudo chown www-data SatTrackerPiWebServer/
sudo systemctl restart sat_tracker_pi_daemon.service 
sudo systemctl restart sat_tracker_pi_web_server.service 
