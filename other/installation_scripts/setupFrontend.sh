#!/bin/bash

echo "moving folder"
cd ../../react-app

echo "installing app"
sudo npm i

echo "building app"
sudo npm run build

echo "serving app"
sudo npm run preview