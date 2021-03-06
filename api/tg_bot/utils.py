#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
import time
import requests
import telebot
from telebot import types
from telebot.util import extract_arguments

from . import constants
from ..common.exceptions import ServiceException
from ..common.clients import EEBookClient, UrlMetadataClient
from ..cache import RedisCache

bot = telebot.TeleBot(os.getenv("TG_BOT_TOKEN", None))
BETA_USER_COUNT = os.getenv("BETA_USER_COUNT", 20)
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
    LOGGER.info("This page: {}".format(this_page))

    if (this_page<0) or (int(page_total) == 0):
        bot.answer_callback_query(callback_query_id=call.id, text='')
    buttons = []
    if this_page > 1:
        buttons.append(
            types.InlineKeyboardButton("⬅️", callback_data="prev:"+action+"_"+resource+"-"+str(this_page)),
        )
    buttons.append(
        types.InlineKeyboardButton(str(this_page), callback_data="current_page"),
    )
    if this_page < int(page_total):
        buttons.append(
            types.InlineKeyboardButton("➡️", callback_data="next:"+action+"_"+resource+"-"+str(this_page)),
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
            token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")
            job_config_result = EEBookClient(token).get_job_config_list(DEFAULT_PAGE_SIZE, page)
            result = get_list_job_config_result(job_config_result, header)
            return result, job_config_result.get("page_total", 0)
        elif res == "job":
            token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")
            jobs_result = EEBookClient(token).get_job_list(DEFAULT_PAGE_SIZE, page, res_name)
            result = get_list_job_result(jobs_result, _header=header)
            return result, jobs_result.get("page_total", 0)
        elif res == "book":
            token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")
            books_result = EEBookClient(token).get_book_list(DEFAULT_PAGE_SIZE, page)
            result = get_list_book_result(books_result, header)
            return result, books_result.get("page_total", 0)
    elif action == "detail":
        if res == "config":
            token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")
            jobs_result = EEBookClient(token).get_job_list(DEFAULT_PAGE_SIZE, page, res_name)
            result = get_list_job_result(jobs_result, _header=header)
            return result, jobs_result.get("page_total", 0)


def list_result(res_id, header, action_type, res_results):
    result2return = header
    for result in res_results["results"]:
        item = str(result[res_id])
        line = action_type + item.replace("-", "_") + "\n"
        result2return = result2return + line
    return result2return


def get_list_book_result(books_result, _header=None):
    if not books_result.get("results", []):
        header = """
抱歉，您没有任何图书。
"""
    else:
        header = """
🎉🎉🎉
您的图书:

"""
    if _header:
        header = _header
    result = list_result("uuid", header, "/detail_book_", books_result)
    return result

def get_list_job_result(jobs_result, _header=None):
    if not jobs_result.get("results", []):
        header = """
抱歉，您还没有任何 job
"""
    else:
        header = """
🎉🎉🎉
您的 jobs:

"""
    if _header:
        header = _header
    result = list_result("job_uuid", header, "/detail_job_", jobs_result)
    return result


def get_list_job_config_result(job_configs, _header=None):
    if not job_configs.get("results", []):
        header = """
抱歉，您还没有进行过提交
"""
    else:
        header = """
🎉🎉🎉
您提交的配置：

"""
    if _header:
        header = _header
    result = list_result("config_name", header, "/detail_config_", job_configs)
    # result = result + "\n Try /detail {{config}} to get the detail"
    return result


def get_detail_job_config_result(config_detail):
    new_config_detail = mk_variable_str(config_detail)
    result = """
您的配置：
{config_name}

创建时间: {created_at}
镜像: {image_name}:{image_tag}
URL: {url}
变量:

{variable_str}

运行该配置:
  /run_config_{config_name}
删除该配置:
  /delete_config_{config_name}
""".format(**new_config_detail)
    return result


def get_detail_job_result(job_detail):
    LOGGER.info("job detail: {}".format(job_detail))
    new_job_detail = mk_variable_str(job_detail)
    new_job_detail["job_uuid"] = new_job_detail["job_uuid"].replace("-", "_")
    result = """
job:
{job_uuid}

配置名称: {config_name}
镜像: {image_name}:{image_tag}
URL: {url}
变量:

{variable_str}

获取配置细节:
  /detail_config_{config_name}
删除 job:
  /delete_job_{job_uuid}
""".format(**new_job_detail)
    return result


def get_detail_book_result(book_detail):
    result = """
🎉🎉🎉
{id}

图书名称: {title}
是否公开: {is_public}
""".format(**book_detail["result"])
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
您可以提交这个 url

名称: {}
描述: {}
仓库: {}
    """.format(info["name"], info["info"], info["repo"], variable_str)
    if variable_str != "\n":
        result = result + "\nVariables:\n{}".format(variable_str)
    return result


def delete_config(token, config_name):
    try:
        EEBookClient(token).delete_job_config(config_name)
        response_str = "Config {} deleted successfully".format(config_name)
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, job config not exist"
        elif s.error_type == "unauthorized":
            response_str = "Hello there, Long time no see."
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
        elif s.error_type == "unauthorized":
            response_str = constants.TOKEN_EXPIRED_STRING
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


def detail_book(token, book_id):
    try:
        result = EEBookClient(token).get_book_detail(book_id)
        response_str = get_detail_book_result(result)
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, book not exist"
        elif s.error_type == "unauthorized":
            response_str = constants.TOKEN_EXPIRED_STRING
        else:
            response_str = "Something wrong, please contact @knarfeh"
    return response_str

def get_book_dl_url(token, book_id):
    try:
        result = EEBookClient(token).get_book_detail(book_id)
        download_url = result["result"]["download_url"]
        book_name = result["result"]["title"]
        return download_url, book_name, True
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, book not exist"
        elif s.error_type == "unauthorized":
            response_str = constants.TOKEN_EXPIRED_STRING
        else:
            response_str = "Something wrong, please contact @knarfeh"
        return response_str, "", False


def download_send_book(url, chat_id, book_name):
    LOGGER.info("Download url: {}, chat_id: {}, book_name: {}".format(url, chat_id, book_name))
    if url == "" or book_name == "":
        bot.send_message(chat_id, "生成电子书失败了，请使用 /logs 查阅日志")
        return
    r = requests.get(url)
    with open("/tmp/{}".format(book_name), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    doc = open('/tmp/{}'.format(book_name), 'rb')
    bot.send_document(chat_id, doc)
    os.remove('/tmp/{}'.format(book_name))


def start_job(token, payload):
    try:
        EEBookClient(token).start_job(payload)
        response_str = "Working on it!"
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, job config not exist"
        elif s.error_type == "unauthorized":
            response_str = "Hello there, Long time no see."
        if s.code == "unknown_issue":
            response_str = "Something wrong, please contact @knarfeh"
    return response_str


def delete_job(token, job_id):
    try:
        EEBookClient(token).delete_job(job_id)
        response_str = "Job: {} deleted successfully".format(job_id)
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, job {} not exist".format(job_id)
        elif s.error_type == "unauthorized":
            response_str = "Hello there, Long time no see."
        else:
            response_str = "Something wrong, please contact @knarfeh"
    LOGGER.info("Delete job %s, response str: %s", job_id, response_str)
    return response_str


def delete_book(token, book_id):
    try:
        EEBookClient(token).delete_book(book_id)
        response_str = "Book: {} deleted successfully".format(book_id)
    except ServiceException as s:
        if s.code == "resource_not_exist":
            response_str = "Ops, book {} not exist".format(book_id)
        elif s.error_type == "unauthorized":
            response_str = "Hello there, Long time no see."
        else:
            response_str = "出了一些错误, 请联系 @knarfeh"
    LOGGER.info("Delete book %s, response str: %s", book_id, response_str)
    return response_str


def get_url_info(payload):
    try:
        url_metadata = UrlMetadataClient.get_url_metadata(payload)
        response_str = get_url_info_result(url_metadata)
    except ServiceException as s:
        if s.code == "url_not_support":
            # TODO: recommend similar url
            response_str = "Url not supported"
        else:
            response_str = "出了一些错误, 请联系 @knarfeh"
    return response_str


def mk_variable_str(detail_dict):
    variable_str = ""
    for item in detail_dict["envvars"]:
        if item["name"] == "URL":
            detail_dict["url"] = item["value"]
        elif item["name"].startswith("_") or item["name"] in ["ES_INDEX", "CREATED_BY"]:
            continue
        else:
            variable_str = variable_str + str(item["name"]) + "=" + str(item["value"]) + "\n"
    detail_dict["variable_str"] = variable_str
    return detail_dict


def check_interval(message, user_id):
    key = "eebook:user_interval:" + str(user_id) + "-tg"
    interval = RedisCache().writer.get(key)
    last_job_time = RedisCache().writer.get("eebook:last_job_time:" + str(user_id) + "-tg")
    if interval is None:
        interval = 86400
    if last_job_time is None:
        last_job_time = -86400
    if int(time.time()) - int(last_job_time) < int(interval):
        bot.reply_to(message, "在过去的24小时内已经运行了一次，请第二天再生成 EPub 文件，如有疑问请询问 @knarfeh")
        return False
    return True


def beta_user_check(user_id):
    now_num = RedisCache().writer.scard("eebook:beta_user")
    if int(now_num) < int(BETA_USER_COUNT):
        RedisCache().writer.sadd("eebook:beta_user", user_id)
        return True
    elif RedisCache().writer.sismember("eebook:beta_user", user_id):
        return True
    return False
