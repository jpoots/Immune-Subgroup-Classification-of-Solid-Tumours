# Dockerfile to define main container aided by  https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xix-deployment-on-docker-containers and chatGPT

# python image
FROM python:3.9-bullseye

# create working dir, set workdir
RUN mkdir /api
WORKDIR /api

# set up software
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app app
COPY main.py main.py
COPY celery_worker.py celery_worker.py
COPY .flaskenv .flaskenv

EXPOSE 3000

CMD [ "gunicorn", "-b", ":3000", "-w", "4", "--access-logfile", "-", "--error-logfile", "-", "main:app" ]