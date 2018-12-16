#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
import copy
import telebot
import hashlib
import time
import dateutil.parser

from flask import request, g, current_app
from telebot import types
from telebot.util import extract_arguments


from . import constants
from . import tg_bot_bp
from ..common.utils import json
from ..users.models import Users, ActivationKeys, EncryptedTokens
from ..users import infra
from ..users.domain import generate_api_token
from ..cache import RedisCache
from ..common.clients import EEBookClient, UrlMetadataClient
from ..common.exceptions import ServiceException
from .utils import (pagination_edit_list_by_category, get_result_by_action_res, delete_config,
                    detail_config, start_job, delete_job,
                    detail_job, get_url_info, delete_book,
                    detail_book, get_book_dl_url, download_send_book,
                    check_interval, beta_user_check
)

bot = telebot.TeleBot(os.getenv("TG_BOT_TOKEN", None))
TG_PASSWORD = os.getenv("TG_PASSWORD", "nopassword")
USER_TOKEN_EXPIRED = os.getenv("USER_TOKEN_EXPIRED", "2147483647")
# USER_TOKEN_EXPIRED = os.getenv("USER_TOKEN_EXPIRED", "3")
LOGGER = logging.getLogger(__name__)
UNKNOWN_ERROR = "Something wrong, please contact @knarfeh"


@tg_bot_bp.route('/webhook', methods=['POST'])
@json
def bot_webhook():
    if request.method == "POST":
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])

        if update.message is not None:
            username = str(update.message.from_user.id)
        else:
            username = str(update.callback_query.message.from_user.id)
        user, token = get_user(username)
        RedisCache().writer.set("eebook:user:"+user.username, token)
        RedisCache().writer.expire("eebook:user:"+user.username, USER_TOKEN_EXPIRED)
        return {}


@tg_bot_bp.route('/job_result', methods=['POST'])
@json
def send_book():
    data = request.json.copy()
    LOGGER.info("Send book, data: {}".format(data))
    download_send_book(data["book_url"], data["chat_id"], data["book_name"])
    return {}


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    if not beta_user_check(message.from_user.id):
        bot.reply_to(message, "内测人数已满")
        return
    bot.reply_to(message, "你好，内测人数未满，文档地址：https://eebook.nujeh.com")


@bot.message_handler(commands=["submit"])
def submit_url(message):
    """
    /submit https://zhuanlan.zhihu.com/newsql
    """
    # http://wiki.jikexueyuan.com/project/explore-python/Standard-Modules/hashlib.html
    if not beta_user_check(message.from_user.id):
        bot.reply_to(message, "内测人数已满")
        return
    if not check_interval(message, message.from_user.id):
        LOGGER.info("User {} run again in 24 hours".format(message.from_user.id))
        return

    submit_str = extract_arguments(message.text.strip())
    if submit_str == "":
        bot.reply_to(message, "请输入一个链接, 比如 /submit http://baidu.com")
        return
    args = submit_str.split(" ")
    if len(args) % 2 == 0:
        args.append(" ")
    url_metadata_payload = { "url": args[0] }
    try:
        url_metadata = UrlMetadataClient.get_url_metadata(url_metadata_payload)
        LOGGER.debug("URL metadata of {}: {}".format(args[0], url_metadata))
    except ServiceException as s:
        if s.code == "url_not_support":
            # TODO: recommend similar url
            response_str = "Url 暂不支持"
        else:
            response_str = UNKNOWN_ERROR
        bot.reply_to(message, response_str)
        return

    submit_env_dict = dict(zip(args[1::2], args[2::2]))
    LOGGER.info("submit_env_dict: {}".format(submit_env_dict))

    if url_metadata["schema"] is not None:
        required_env_list = url_metadata["schema"].get("required", [])
        properties = url_metadata["schema"].get("properties", {})
        default_env_dict = [{"name": k, "value": v["default"]} for k, v in properties.items() if v.get("default", None) and k not in submit_env_dict.keys()]
    else:
        required_env_list = list()
        default_env_dict = dict()
    missed_env = [item for item in required_env_list if item not in submit_env_dict.keys()]
    LOGGER.info('default_env_dict: {}'.format(default_env_dict))
    if len(missed_env) > 0:
        bot.reply_to(message, ", ".join(missed_env) + " is required")
        return
    config_name = hashlib.md5((submit_str+str(message.from_user.id)+"-tg").encode('utf-8')).hexdigest()
    envvars = [{"name": k, "value": v} for k, v in submit_env_dict.items()]
    envvars.append({"name": "URL", "value": args[0]})
    envvars.append({"name": "_CHAT_ID", "value": str(message.chat.id)})
    envvars.append({"name": "ES_INDEX", "value": url_metadata["name"]})
    envvars.append({"name": "CREATED_BY", "value": str(message.from_user.id)+"-tg"})
    for item in default_env_dict:
        envvars.append({"name": item["name"], "value": item["value"]})
    job_config_payload = {
        "config_name": config_name,
        "image_name": url_metadata["image"],
        "created_by": str(message.from_user.id)+"-tg",
        "envvars": envvars
    }
    LOGGER.info("Creating job config, payload: {}".format(job_config_payload))
    token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")
    try:
        EEBookClient(token).create_job_config(job_config_payload)
    except ServiceException as e:
        if e.code == "job_config_name_conflict":
            response_str = "该提交已存在，请使用 /run_config_{} 运行\n，输入 /detail_config_{} 查看已经运行的提交".format(
                config_name, config_name)
        else:
            response_str = UNKNOWN_ERROR
        LOGGER.info("Create job config, response string: {}".format(response_str))
        bot.reply_to(message, response_str)
        return
    start_job_payload = {
        "config_name": config_name
    }
    response_str = start_job(token, start_job_payload)
    LOGGER.info("Start a job, response string: %s", response_str)
    bot.reply_to(message, response_str)
    if response_str == "工作中...":
        LOGGER.debug("Setting last running job")
    RedisCache().writer.set("eebook:last_job_time:" + str(message.from_user.id) + "-tg", int(time.time()))
    return


@bot.message_handler(commands=["url_info"])
def url_info(message):
    """
    /url_info http://baidu.com
    """
    url = extract_arguments(message.text.strip())
    LOGGER.info("Get url info, url: %s", url)
    if url == "":
        bot.reply_to(message, "请输入一个 url, 比如 /url_info http://baidu.com")
        return
    data = { "url": url }
    response_str = get_url_info(data)
    LOGGER.info("Response string: %s", response_str)
    bot.reply_to(message, response_str, disable_web_page_preview=True)


@bot.message_handler(commands=["example", "examples"])
def url_example_by_type(message):
    # TODO
    pass


@bot.message_handler(commands=["list"])
def list_resource(message):
    """
    Get a list of job config, job, books
    /list
    /list config
    /list config config_name list job of config_name

    /list job list all jobs
    /list jobs list all jobs

    /list book
    /list books
    """
    if not beta_user_check(message.from_user.id):
        bot.reply_to(message, "内测人数已满")
        return
    submit_str = extract_arguments(message.text.strip())
    args = submit_str.split(" ")
    markup = types.InlineKeyboardMarkup()

    if args[0] == "config" or args[0] == "configs":
        LOGGER.info("List configs")
        result, page_total = get_result_by_action_res(message, "list", "config", 1)
        if int(page_total) >= 2:
            markup.add(
                types.InlineKeyboardButton("1", callback_data="current_page:"),
                types.InlineKeyboardButton("➡️", callback_data="next:list_config-1")
            )
        LOGGER.info("List config, result: {}".format(result))
    elif args[0] == "job" or args[0] == "jobs":
        LOGGER.info("List jobs")
        result, page_total = get_result_by_action_res(message, "list", "job", 1)
        if int(page_total) >= 2:
            markup.add(
                types.InlineKeyboardButton("1", callback_data="current_page:"),
                types.InlineKeyboardButton("➡️", callback_data="next:list_job-1")
            )
        LOGGER.info("List jobs, result: {}".format(result))
    elif args[0] == "book" or args[0] == "books":
        LOGGER.info("List books, TODO")
        result, page_total = get_result_by_action_res(message, "list", "book", 1)
        if int(page_total) >= 2:
            markup.add(
                types.InlineKeyboardButton("1", callback_data="current_page:"),
                types.InlineKeyboardButton("➡️", callback_data="next:list_book-1")
            )
        LOGGER.info("List books, result: {}".format(result))
    elif args[0] == "":
        LOGGER.info("/list")
        result = "/list_config \n/list_job \n/list_book \n"
    else:
        result = "输入了暂不支持的资源类型"
    bot.reply_to(message, result, reply_markup=markup)


@bot.message_handler(commands=["detail"])
def get_resource(message):
    """
    get details of a resource
    /detail_config
    /detail_job
    /detail_book
    """
    if not beta_user_check(message.from_user.id):
        bot.reply_to(message, "内测人数已满")
        return

    submit_str = extract_arguments(message.text.strip())
    args = submit_str.split(" ")
    token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")
    markup = types.InlineKeyboardMarkup()

    if args[0] == "config" or args[0] == "configs":
        if len(args) == 1:
            LOGGER.info("no config name, list /detail_config_name")
            result, page_total = get_result_by_action_res(message, "list", "config", 1)
            if int(page_total) >= 2:
                markup.add(
                    types.InlineKeyboardButton("1", callback_data="current_page:"),
                    types.InlineKeyboardButton("➡️", callback_data="next:list_config-1")
                )
        else:
            config_detail_result = detail_config(token, args[1])
            if config_detail_result == constants.TOKEN_EXPIRED_STRING:
                result = config_detail_result
            else:
                config_jobs_result, page_total = get_result_by_action_res(message, "detail", "config", 1, res_name=args[1], header="{} 的 jobs:\n".format(args[1]))
                if int(page_total) != 0 and int(page_total) != 1:
                    markup.add(
                        types.InlineKeyboardButton("1", callback_data="current_page:"),
                        types.InlineKeyboardButton("➡️", callback_data="next:detail_config/{}-1".format(args[1]))
                    )
                LOGGER.info("List config {}, config_detail_result: {}".format(args[1], config_jobs_result))
                LOGGER.info("List config {}, result: {}".format(args[1], config_jobs_result))
                result = config_detail_result + "\n" + config_jobs_result
        LOGGER.debug("Got detailed config result: {}, args: {}".format(result, args))
    elif args[0] == "job" or args[0] == "jobs":
        if len(args) == 1:
            LOGGER.info("no job id, list /detail_job_id")
            job_detail_result = ""
            jobs_result, page_total = get_result_by_action_res(message, "list", "job", 1)
            if int(page_total) >= 2:
                markup.add(
                    types.InlineKeyboardButton("1", callback_data="current_page:"),
                    types.InlineKeyboardButton("➡️", callback_data="next:list_job-1")
                )
        else:
            job_id = "-".join(args[1:])
            LOGGER.info("Get detail of job %s", job_id)
            job_detail_result = detail_job(token, job_id)
            # jobs_result = "/delete_job_" + job_id.replace("-", "_")
        # result = job_detail_result + "\n" + jobs_result
        result = job_detail_result
        LOGGER.debug("Got detailed job result: {}, args: {}".format(result, args))
    elif args[0] == "book" or args[0] == "books":
        if len(args) == 1:
            LOGGER.info("no book id, list /detail_book_id")
            book_detail_result = ""
            books_result, page_total = get_result_by_action_res(message, "list", "book", 1)
            if int(page_total) >= 2:
                markup.add(
                    types.InlineKeyboardButton("1", callback_data="current_page:"),
                    types.InlineKeyboardButton("➡️", callback_data="next:list_book-1")
                )
        else:
            book_id = "-".join(args[1:])
            LOGGER.info("Get detail of book: %s", book_id)
            # book_detail_result = detail_book(token, book_id)
            book_detail_result = None
            # books_result = "/delete_book_" + book_id.replace("-", "_")
            books_result = "None"
            books_result = books_result + "\n/dl_book_" + book_id.replace("-", "_")
        result = book_detail_result + "\n" + books_result
        LOGGER.info("Got detailed book result: {}, args: {}".format(result, args))
    elif args[0] == "":
        result = "/detail_config \n /detail_job \n /detail_book"
    else:
        print("TODO")
    bot.reply_to(message, result, reply_markup=markup, disable_web_page_preview=True)


@bot.message_handler(commands=["delete"])
def delete_resource(message):
    """
    Delete a resource
    /delete config
    /delete job
    /delete book
    """
    if not beta_user_check(message.from_user.id):
        bot.reply_to(message, "内测人数已满")
        return
    submit_str = extract_arguments(message.text.strip())
    args = submit_str.split(" ")
    if len(args) < 2:
        LOGGER.info("请指定要删除的资源名称")
    token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")

    if args[0] == "config":
        LOGGER.info("Delete config %s", args[1])
        response_str = delete_config(token, args[1])
    elif args[0] == "job" or args[0] == "jobs":
        job_id = "-".join(args[1:])
        LOGGER.info("Delete job: %s", job_id)
        response_str = delete_job(token, job_id)
    elif args[0] == "books" or args[0] == "book":
        book_id = "-".join(args[1:])
        LOGGER.info("Delete book: %s", book_id)
        response_str = delete_book(token, book_id)
    elif args[0] == "":
        response_str = "/delete_config \n /delete_job \n /delete_book"
    LOGGER.info("Delete resource, args[0]: {}, response_str: {}".format(args[0], response_str))
    bot.reply_to(message, response_str)
    return


@bot.message_handler(commands=["edit", "update"])
def update_resource(message):
    """
    edit job config, book
    /edit config
    /edit book
    """
    LOGGER.info("TODO, edit")
    bot.reply_to(message, "编辑已有的提交，WIP")
    return


@bot.message_handler(commands=["run"])
def run_job(message):
    """
    run job with job config or job id
    /run job_config or job_uuid
    /run_config_name
    """
    if not check_interval(message, message.from_user.id):
        LOGGER.info("User {} run again in 24 hours".format(message.from_user.id))
        return
    submit_str = extract_arguments(message.text.strip())
    if submit_str == "":
        return
    args = submit_str.split(" ")
    if len(args) < 2:
        LOGGER.info("请指定要运行的一次提交")
    token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")

    if args[0] == "config":
        payload = {
            "config_name": args[1]
        }
        response_str = start_job(token, payload)
        LOGGER.info("Start a job, response string: %s", response_str)
    bot.reply_to(message, response_str)


@bot.message_handler(commands=["supported"])
def supported_url(message):
    """
    Get supported url
    Need improvement
    /supported
    """
    # TODO: webpreview
    LOGGER.info("Get supported url, message: {}".foramt(message))
    bot.reply_to(message, "https://eebook.github.io/catalog/")


@bot.message_handler(commands=["logs"])
def job_logs(message):
    """
    get logs of a job
    /logs                   get logs of latest job
    /logs job_uuid          get logs of a job
    /logs 20                get 20 log of latest job
    /logs job_uuid 20       get 20 logs of a specific job
    """
    bot.reply_to(message, "获取最近运行的提交的日志")
    token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")
    jobs_result = EEBookClient(token).get_job_list(1, 1, None)
    if not jobs_result.get("results", []):
        bot.reply_to(message, "抱歉，您没有任何提交")
        return
    results = jobs_result.get("results")
    job_uuid = results[0]["job_uuid"]
    started_at = results[0]["started_at"]
    LOGGER.info("started_at: {}, job_uuid: {}".format(started_at, job_uuid))
    start_time = int(time.mktime(dateutil.parser.parse(started_at).timetuple()))
    end_time = int(start_time + 7200)
    try:
        logs = EEBookClient(token).get_job_logs(job_uuid, start_time, end_time, 1)
    except Exception as e:
        response_str = UNKNOWN_ERROR
        bot.reply_to(message, response_str)
        return
    result = ""
    for item in sorted(logs["results"], key=lambda k: k["timestamp"]):
        result = result + item["timestamp"] + ": " + item["log"]
    with open("/tmp/{}.log".format(job_uuid), "w") as text_file:
        text_file.write(result)
    log_file = open("/tmp/{}.log".format(job_uuid), "rb")
    bot.send_document(message.chat.id, log_file)
    os.remove('/tmp/{}.log'.format(job_uuid))


@bot.message_handler(commands=["report"])
def report_issue(message):
    """
    report an issue
    /report url  report url git repo, git issue
    /report contact @knarfeh
    """
    # TODO
    pass


@bot.message_handler(commands=["dl"])
def download_book(message):
    """
    /dl_book_id
    """
    submit_str = extract_arguments(message.text.strip())
    args = submit_str.split(" ")
    token = RedisCache().writer.get("eebook:user:" + str(message.from_user.id) + "-tg")
    if args[0] == "book":
        if len(args) == 1:
            result = "请指定 book id"
            bot.reply_to(message, result)
        else:
            book_id = "-".join(args[1:])
            LOGGER.info("Get book %s to download", book_id)
            url_or_res, book_name, success = get_book_dl_url(token, book_id)
            LOGGER.info("url_or_res: {}, book_name: {}, success: {}".format(url_or_res, book_name, success))
            if success:
                download_send_book(url_or_res, message.chat.id, book_name)
                return
            bot.reply_to(message, url_or_res)

    else:
        result = "TODO: list all dl_book_id"
        bot.reply_to(message, result)


@bot.message_handler(commands=["search"])
def donate(message):
    """
    search books
    """
    # TODO
    pass


@bot.message_handler(commands=["settings"])
def settings(message):
    """
    settings, including language, search feature(本站搜索，全网搜索)
    """
    # TODO
    pass


@bot.message_handler(commands=["kindle"])
def kindle(message):
    """
    kindle
    """
    pass


@bot.message_handler(commands=["donate"])
def donate(message):
    """
    """
    # TODO
    pass


# admin command
@bot.message_handler(commands=["interval"])
def user_interval(message):
    username = message.from_user.username
    if username != os.getenv("TG_ADMIN", "knarfeh"):
        bot.reply_to(message, "Sorry, you are not admin")
        return
    submit_str = extract_arguments(message.text.strip())
    args = submit_str.split(" ")
    if len(args) < 2:
        bot.reply_to(message, "Not enough args")
        return
    key = "eebook:user_interval:" + str(args[0].strip()) + "-tg"
    value = int(args[1], 10)
    RedisCache().writer.set(key, value)
    bot.reply_to(message, "Set {} intervals to {}".format(key, value))


# admin command
@bot.message_handler(commands=["list_all_interval"])
def list_all_interval(message):
    username = message.from_user.username
    if username != os.getenv("TG_ADMIN", "knarfeh"):
        bot.reply_to(message, "Sorry, you are not admin")
        return
    bot.reply_to(message, "list all interval")


@bot.callback_query_handler(func=lambda call: True)
def process_callback_button(call):
    operator, query = call.data.split(":")
    if operator in ["prev", "next"]:
        LOGGER.info("pagination_edit_list_by_category")
        pagination_edit_list_by_category(call, operator, query)
    elif operator == "current_page":
        bot.answer_callback_query(callback_query_id=call.id, text='')


@bot.message_handler(func=lambda message: True)
def other_message(message):
    new_message_json = message.json
    cmd_args = new_message_json["text"].split("_")
    LOGGER.info("Handle other message, cmd_args: {}".format(cmd_args))
    supported_cmd = [
        "/list",
        "/detail",
        "/delete",
        "/dl",
        "/run",
    ]
    if cmd_args[0].startswith("/") and cmd_args[0] not in supported_cmd:
        result = "Unsupported command"
        bot.reply_to(message, result)
        return
    elif cmd_args[0].startswith("/") and cmd_args[0] in supported_cmd:
        new_message_json["text"] = " ".join(cmd_args)
        new_message = types.Message.de_json(new_message_json)
        bot.process_new_messages([new_message])
    # else:
	    # bot.reply_to(message, "TODO: search book command???")


# Utils
def get_user(_username):
    """
    if not exist, create user
    """
    user = Users.query.filter_by(username=_username+"-tg").first()
    if not user:
        LOGGER.info("User {} not exist, creating".format(_username))
        username = _username + "-tg"
        email = "tg_user_{}@eebook.com".format(_username)
        user_dict = {
            "username": username,
            "email": email,
            "password": TG_PASSWORD,
            "is_active": False
        }
        user = infra.create_user(user_dict)
        ActivationKeys.query.filter_by(user_id=user.id).first().delete()
        token = generate_api_token(user_dict, need_user_active=False)['token']
        RedisCache().writer.set("eebook:user:"+username, token)
        RedisCache().writer.expire("eebook:user:"+username, USER_TOKEN_EXPIRED)
    token = EncryptedTokens.get_or_create(defaults=None, user_id=user.id)[0].key
    return user, token
