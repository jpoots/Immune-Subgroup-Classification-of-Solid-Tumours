#!/bin/bash

echo "MOVING LOCATION"
cd ../../react-app

echo "STARTING FRONTEND ON PORT 5173"
docker run --name react-app -p 5173:5173 --rm react-app