#!/bin/bash

echo "moving"
cd ../../api

echo "setting up venv"
python3 -m venv .venv
source .venv/bin/activate

echo "installing dependencies"
pip install -r requirements.txt


mysql.server stop
mysql.server start

echo "starting app"
gunicorn -b localhost:3000 -w 1 main:app
