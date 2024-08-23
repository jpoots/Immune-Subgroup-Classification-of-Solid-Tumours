#!/bin/bash

cd ../../api
source .venv/bin/activate

echo "starting celery worker"

celery -A celery_worker.celery worker --pool=threads --loglevel=INFO