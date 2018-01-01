sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:gpredict-team/ppa
sudo apt-get update

sudo pip install future

cd ~/src/git/IndustrialAutomation/RadioAntenna/PiCode/
git clone https://github.com/adafruit/Adafruit_Python_PCA9685.git

git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git
cd Adafruit-Motor-HAT-Python-Library

sudo apt-get install python-dev

sudo python setup.py install