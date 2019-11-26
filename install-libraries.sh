# GOOSE needs Python 3 and some libraries
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install --upgrade setuptools
sudo apt-get install libpng-dev libfreetype6-dev
sudo pip3 install numpy
sudo pip3 install matplotlib
sudo pip3 install cairocffi
sudo pip3 install pycryptodome

# Apache Jena needs Java
sudo apt-get install openjdk-8-jre-headless

# gMark needs C++
sudo apt-get install g++
