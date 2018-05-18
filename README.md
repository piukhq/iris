# iris

Content delivery API with dynamic image resizing.

## Installation

```shell
pipenv install --dev
```

## Test Server

```shell
pipenv shell
flask run
```

```shell
http get localhost:5000/path/to/image.jpg?width=300&height=200
```

## Run Load Test

```shell
pipenv shell
python lt.py
```
