#!/bin/bash

echo "moving"
cd ../../api

echo "BUILDING CONTAINERS....."
sudo docker compose build
echo "DONE"
