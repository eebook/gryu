FROM python:3.6.0rc2-alpine
MAINTAINER He Jun knarfeh@outlook.com

# base pkgs
RUN apk --update add --no-cache openssl ca-certificates postgresql-dev

# build pkgs
RUN apk --update add gcc g++ python3-dev musl-dev

# dev pkgs
RUN apk add curl

COPY requirements /requirements
RUN pip3 install -U pip \
    && pip install -i https://pypi.douban.com/simple -r requirements/dev.txt

WORKDIR /src