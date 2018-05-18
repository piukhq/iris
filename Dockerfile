FROM python:3.6

WORKDIR /app
COPY . .

RUN pip install pipenv && pipenv install --system
