#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals


import logging
import telebot
import os
from flask import request, g, current_app
from . import tg_bot_bp
from ..common.utils import json

LOGGER = logging.getLogger(__name__)
bot = telebot.TeleBot(os.getenv("TG_BOT_TOKEN", None))
# bot.set_webhook(url=os.getenv("TG_WEBHOOK_URL", "https://gryuint.nujeh.com/tg_bot/webhook"))

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

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    LOGGER.info("message??? {}".format(message))
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))
