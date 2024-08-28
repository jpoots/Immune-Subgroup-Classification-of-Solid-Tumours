#!/bin/bash

cd ../../api
source .venv/bin/activate

echo "starting app"
gunicorn -b localhost:3000 -w 1 main:app

