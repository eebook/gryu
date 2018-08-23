#!/bin/sh
python manage.py db upgrade
supervisord --nodaemon -c /src/etc/supervisord.conf
