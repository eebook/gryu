#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
import telebot

from telebot import types
from telebot.util import extract_arguments
from ..common.exceptions import ServiceException
from ..common.clients import EEBookClient
from ..cache import RedisCache

bot = telebot.TeleBot(os.getenv("TG_BOT_TOKEN", None))
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", 2))
LOGGER = logging.getLogger(__name__)


def pagination_edit_list_by_category(call, operator, query):
    LOGGER.info("Pagination, operator: {}, query: {}".format(operator, query))
    category, current_page = query.split("-")
    action, resource = category.split("_")
    resource_list = resource.split("/")
    resource_type, resource_name = resource_list if len(resource_list) == 2 else [resource_list[0], None]
    if operator == "prev":
        this_page = int(current_page) - 1
    elif operator == "next":
        this_page = int(current_page) + 1
    result, page_total = get_result_by_action_res(call, action, resource_type, this_page, resource_name)
    LOGGER.info("Total page: {}".format(page_total))
    LOGGER.info("this_page: {}".format(this_page))

    if (this_page<0) or (int(page_total) == 0):
        bot.answer_callback_query(callback_query_id=call.id, text='')
    buttons = []
    if this_page > 1:
        buttons.append(
            types.InlineKeyboardButton("<<", callback_data="prev:"+action+"_"+resource+"-"+str(this_page)),
        )
    buttons.append(
        types.InlineKeyboardButton(str(this_page), callback_data="current_page"),
    )
    if this_page < int(page_total):
        buttons.append(
            types.InlineKeyboardButton(">>", callback_data="next:"+action+"_"+resource+"-"+str(this_page)),
        )
    markup = types.InlineKeyboardMarkup()
    markup.add(*buttons)
    bot.edit_message_text(
        result,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(callback_query_id=call.id, text='')


def get_result_by_action_res(message, action, res, page, res_name=None, header=None):
    if action == "list":
        if res == "config":
            token = RedisCache().writer.get("eebook-gryu-" + message.from_user.username + "-tg")
            job_config_result = EEBookClient(token).get_job_config_list(DEFAULT_PAGE_SIZE, page)
            result = get_list_job_config_result(job_config_result, header)
            return result, job_config_result.get("page_total", 0)
        elif res == "job":
            token = RedisCache().writer.get("eebook-gryu-" + message.from_user.username + "-tg")
            jobs_result = EEBookClient(token).get_job_list(DEFAULT_PAGE_SIZE, page, res_name)
            result = get_list_job_result(jobs_result, _header=header)
            return result, jobs_result.get("page_total", 0)
    elif action == "detail":
        if res == "config":
            token = RedisCache().writer.get("eebook-gryu-" + message.from_user.username + "-tg")
            jobs_result = EEBookClient(token).get_job_list(DEFAULT_PAGE_SIZE, page, res_name)
            LOGGER.info("jobs_result???{}".format(jobs_result))
            result = get_list_job_result(jobs_result, _header=header)
            return result, jobs_result.get("page_total", 0)


def list_result(res_id, header, action_type, res_results):
    result2return = header
    for result in res_results["results"]:
        item = str(result[res_id])
        line = item[:8] + " " + action_type + item.replace("-", "_") + "\n"
        result2return = result2return + line
    return result2return

def get_list_job_result(jobs_result, _header=None):
    if not jobs_result.get("results", []):
        header = """
Sorry, you don't have any jobs.
"""
    else:
        header = """
🎉🎉🎉
Your jobs:

"""
    if _header:
        header = _header
    result = list_result("job_uuid", header, "/detail_job_", jobs_result)
    return result


def get_list_job_config_result(job_configs, _header=None):
    if not job_configs.get("results", []):
        header = """
Sorry, you don't have any job config.
"""
    else:
        header = """
🎉🎉🎉
Your job configs:

"""
    if _header:
        header = _header
    result = list_result("config_name", header, "/detail_config_", job_configs)
    # result = result + "\n Try /detail {{config}} to get the detail"
    return result


def get_detail_job_config_result(config_detail):
    new_config_detail = mk_variable_str(config_detail)
    result = """
🎉🎉🎉
{config_name}

Created at: {created_at}
Image: {image_name}:{image_tag}
URL: {url}
Variables:
{variable_str}
""".format(**new_config_detail)
    return result


def get_detail_job_result(job_detail):
    LOGGER.info("job detail: {}".format(job_detail))
    new_job_detail = mk_variable_str(job_detail)
    result = """
🎉🎉🎉
{job_uuid}

Config Name: {config_name}, /detail_config_{config_name}
Image: {image_name}:{image_tag}
URL: {url}
Variables:
{variable_str}
""".format(**new_job_detail)
    return result


def get_url_info_result(info):
    if info["schema"] is not None:
        env_dict = info["schema"].get("properties", {})
    else:
        env_dict = dict()

    variable_str = "\n"
    for key in env_dict.keys():
        default = env_dict[key].get("default", "REQUIRED")
        variable_str = variable_str + key + " " + str(default) + "\n"
    result = """
🎉🎉🎉
Yes, you can submit this url

Name: {}
Description: {}
Repository: {}
Variables:
{}

    """.format(info["name"], info["info"], info["repo"], variable_str)
    return result


def delete_config(token, config_name):
    try:
        EEBookClient(token).delete_job_config(config_name)
        response_str = "Successfully deleted config {}".format(config_name)
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, job config not exist"
        else:
            response_str = "Something wrong, please contact @knarfeh"
    LOGGER.info("Delete config %s, response str: %s", config_name, response_str)
    return response_str


def detail_config(token, config_name):
    try:
        result = EEBookClient(token).get_job_config_detail(config_name)
        response_str = get_detail_job_config_result(result)
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, job config not exist"
        else:
            response_str = "Something wrong, please contact @knarfeh"
    LOGGER.info("Get detailed config %s, response str: %s", config_name, response_str)
    return response_str


def detail_job(token, job_id):
    try:
        result = EEBookClient(token).get_job_detail(job_id)
        response_str = get_detail_job_result(result)
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, job not exist"
        else:
            response_str = "Something wrong, please contact @knarfeh"
    LOGGER.info("Get detailed job %s, response str: %s", job_id, response_str)
    return response_str


def start_job(token, payload):
    try:
        EEBookClient(token).start_job(payload)
        response_str = "Working on it!"
    except ServiceException as e:
        if e.code == "unknown_issue":
            response_str = "Something wrong, please contact @knarfeh"
    return response_str


def delete_job(token, job_id):
    try:
        EEBookClient(token).delete_job(job_id)
        response_str = "Successfully deleted job: {}".format(job_id)
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, job {} not exist".format(job_id)
        else:
            response_str = "Something wrong, please contact @knarfeh"
    LOGGER.info("Delete job %s, response str: %s", job_id, response_str)
    return response_str


def mk_variable_str(detail_dict):
    variable_str = ""
    for item in detail_dict["envvars"]:
        if item["name"] == "URL":
            detail_dict["url"] = item["value"]
        else:
            variable_str = variable_str + item["name"] + "=" + item["value"] + "\n"
    detail_dict["variable_str"] = variable_str
    return detail_dict
