#!/bin/bash

echo "moving"
cd ../../api

echo "BUILDING CONTAINERS....."
docker compose build
echo "DONE"
