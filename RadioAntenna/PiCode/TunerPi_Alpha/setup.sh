cd ~ 
sudo apt-get install socat
sudo apt-get install nginx
sudo apt-get install python3-serial

sudo pip install pyserial
sudo pip install adafruit-circuitpython-mcp3xxx
sudo pip install board
sudo pip install argparse
sudo pip install flask
sudo pip install flask-migrate

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


