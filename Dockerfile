FROM python:3.6

WORKDIR /app
COPY . .

RUN pip install uwsgi pipenv && pipenv install --system --deploy
