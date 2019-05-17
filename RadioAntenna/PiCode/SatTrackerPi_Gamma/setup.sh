sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:gpredict-team/ppa
sudo apt-get update

sudo pip install future
sudo pip install flask
sudo pip install flask_sqlalchemy
sudo pip install flask_migrate

sudo pip install Adafruit_GPIO
sudo pip install Adafruit_MotorHAT
sudo pip install mcp3208


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

sudo apt-get install python-dev

sudo python setup.py install