#!/bin/bash
exec gunicorn -b :3000 -w 4 --access-logfile - --error-logfile - main:app