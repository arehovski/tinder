FROM python:3.9.1-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev zlib-dev jpeg-dev

RUN apk add \
    --no-cache \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    binutils proj gdal geos gdal-dev geos-dev

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["/app/entrypoint.sh"]