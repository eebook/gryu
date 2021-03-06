FROM python:3.6.0rc2-alpine
LABEL maintainer="knarfeh@outlook.com"

# base pkgs
RUN apk --update add --no-cache openssl ca-certificates postgresql-dev nginx supervisor

# build pkgs
RUN apk --update add gcc g++ python3-dev musl-dev make

# dev pkgs
RUN apk --update add curl jq

COPY requirements /requirements
RUN mkdir -p /var/log/eebook
RUN pip3 install -U pip \
    && pip install -i https://pypi.douban.com/simple -r requirements/dev.txt \
    && pip install gunicorn==19.6.0
COPY . /src/

WORKDIR /src
HEALTHCHECK --interval=60s --timeout=5s --retries=5 CMD curl -H "Content-Type: application/json" -s "http://localhost:80/v1/_diagnose" | jq -r -e '.status=="OK"'
CMD chmod u+x /src/run.sh
CMD ["/src/run.sh"]