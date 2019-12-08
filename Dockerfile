FROM python:3.7-alpine

WORKDIR /app
COPY . .

RUN apk add --no-cache --virtual build \
      zlib-dev \
      build-base && \
    apk add --no-cache jpeg-dev && \
    pip install gunicorn pipenv && pipenv install --system --deploy && \
    apk del --no-cache build

CMD ["/usr/local/bin/gunicorn", "-c", "gunicorn.py", "wsgi:app"]
