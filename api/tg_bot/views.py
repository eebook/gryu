#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals


import logging
import telebot
from flask import request, g, current_app
from . import tg_bot_bp
from ..common.utils import json
from .message_handler import bot

LOGGER = logging.getLogger(__name__)


@tg_bot_bp.route('/webhook', methods=['POST'])
@json
def bot_webhook():
    if request.method == "POST":
        LOGGER.info("post")
        data = request.json
        LOGGER.info("data: {}".format(data))
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return {}
