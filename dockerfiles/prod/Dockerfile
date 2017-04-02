FROM python:3.6.0rc2-alpine
MAINTAINER He Jun knarfeh@outlook.com

# basic dependencies
RUN apk --update add --no-cache linux-headers \
                       openssl \
                       ca-certificates \
                       postgresql-dev

RUN apk --update add --no-cache --virtual \
    build-deps \
    gcc \
    g++ \
    python3-dev \
    musl-dev \
    nginx \
    && pip3 install -U pip \
    && pip install uwsgi supervisor \
    && apk del build-deps

RUN mkdir /etc/ee-book-api
COPY conf/* /etc/ee-book-api/
EXPOSE 80 8080 

WORKDIR /src

COPY src /src
ENTRYPORINT ["supervisord"]
CMD ["-c", "/etc/ee-book-api/supervisord.conf"]
