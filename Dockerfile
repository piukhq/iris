FROM binkhq/python:3.9

WORKDIR /app
ADD . .

RUN apt-get update && \
    apt-get install --no-install-recommends -y zlib1g-dev libjpeg-dev && \
    pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --ignore-pipfile && \
    apt-get autoremove -y zlib1g-dev libjpeg-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists

CMD [ "gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", \
                  "--logger-class=iris.gunicorn.Logger", \
                  "--access-logfile=-", "--bind=0.0.0.0:9000", "wsgi:app" ]
