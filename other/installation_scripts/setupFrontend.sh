#!/bin/bash

echo "MOVING LOCATION...."
cd ../../react-app

echo "BUILDING IMAGE..."
sudo docker build -t react-app .

echo "SUCCESS"