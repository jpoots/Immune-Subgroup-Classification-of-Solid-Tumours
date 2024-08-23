#!/bin/bash
sudo apt update

sudo apt install -y redis-server=6.2.*
sudo apt install -y mysql-server=8.0.*

curl -fsSL https://deb.nodesource.com/setup_20.x -o nodesource_setup.sh
sudo -E bash nodesource_setup.sh
sudo apt-get install -y nodejs

sudo systemctl start redis-server
sudo systemctl enable redis-server


sudo systemctl start mysql
sudo systemctl enable mysql