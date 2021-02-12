FROM binkhq/python:3.8

WORKDIR /app
COPY Pipfile.lock Pipfile /app/

RUN apt-get update && \
    apt-get install --no-install-recommends -y zlib1g-dev libjpeg-dev && \
    pip install --no-cache-dir gunicorn pipenv==2018.11.26 && \
    pipenv install --system --deploy --ignore-pipfile && \
    apt-get autoremove -y zlib1g-dev libjpeg-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists

COPY iris /app/iris/

CMD [ "gunicorn", "--workers=2", "--threads=2", "--error-logfile=-", \
                  "--logger-class=iris.gunicorn.Logger", \
                  "--access-logfile=-", "--bind=0.0.0.0:9000", "wsgi:app" ]
