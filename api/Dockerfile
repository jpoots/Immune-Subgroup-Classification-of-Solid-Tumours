FROM python:3.9-bullseye
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app app
COPY main.py main.py
COPY celery_worker.py celery_worker.py
COPY .flaskenv .flaskenv
COPY boot.sh boot.sh
RUN chmod a+x boot.sh

EXPOSE 3000
ENTRYPOINT [ "./boot.sh" ]