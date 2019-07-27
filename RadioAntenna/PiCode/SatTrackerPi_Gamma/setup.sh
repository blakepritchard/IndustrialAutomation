sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:gpredict-team/ppa
sudo apt-get update

sudo pip3 install future
sudo pip3 install flask
sudo pip3 install flask_sqlalchemy
sudo pip3 install flask_migrate

sudo pip3 install Adafruit_GPIO
sudo pip3 install Adafruit_MotorHAT
sudo pip3 install mcp3208


cd ~/
mkdir ~/src
mkdir ~/src/git

cd ~/src/git/
git clone https://github.com/blakepritchard/IndustrialAutomation.git

cd ~/src/git/IndustrialAutomation/RadioAntenna/PiCode/
git clone https://github.com/adafruit/Adafruit_Python_PCA9685.git

git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git
cd Adafruit-Motor-HAT-Python-Library

sudo chown www-data ~/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite
sudo chown www-data ~/src/git/IndustrialAutomation/RadioAntenna/PiCode/SatTrackerPi_Gamma/SatTrackerPiWebsite/app.db

sudo apt-get install python3-dev

sudo python3 setup.py install
