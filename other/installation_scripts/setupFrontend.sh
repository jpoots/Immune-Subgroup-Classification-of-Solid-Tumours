#!/bin/bash

echo "MOVING LOCATION...."
cd ../../react-app

echo "BUILDING IMAGE..."
docker build -t react-app .

echo "SUCCESS"