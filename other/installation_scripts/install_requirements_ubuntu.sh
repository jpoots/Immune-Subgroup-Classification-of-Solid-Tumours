#!/bin/bash
sudo apt update

sudo apt install -y redis=5:6.0.16-1ubuntu1
sudo apt install -y mysql-server=8.0.39-0ubuntu0.22.04.1

curl -fsSL https://deb.nodesource.com/setup_20.x -o nodesource_setup.sh
sudo -E bash nodesource_setup.sh
sudo apt install -y nodejs

sudo systemctl start redis-server
sudo systemctl enable redis-server


sudo systemctl start mysql
sudo systemctl enable mysql