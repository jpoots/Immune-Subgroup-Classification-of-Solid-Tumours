#!/bin/bash

echo "MOVING LOCATION...."
cd ../../react-app

echo "INSTALLING APP..."
sudo npm i

echo "BUILDING APP..."
sudo npm run build

echo "LAUNCHING PREVIEW..."
sudo npm run preview