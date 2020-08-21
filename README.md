# iris

Content delivery API with dynamic image resizing.

## Installation

```shell
pipenv install --dev
```

## Test Server

```shell
export STORAGE_ACCOUNT_CONNECTION_STRING=BLAH
export STORAGE_CONTAINER=BLAH
pipenv run python iris/__init__.py
```

```shell
http get localhost:5000/path/to/image.jpg?width=300&height=200
```

## Run Load Test

```shell
pipenv shell
python lt.py
```
