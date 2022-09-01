# -*- coding: utf-8 -*-
import logging
import traceback
import json
from flask import Blueprint
from flask import request, render_template, jsonify
from config_api import APIMixin
from application import app_config as config

logger = logging.getLogger('easy_http.config_api.group_views')
mod = Blueprint('/group', __name__, url_prefix='/group')


@mod.route("/", methods=['GET'])
def index():
    configs = []
    try:
        configs = config.co_config_group.get_all(all=False)
    except Exception as e:
        logger.debug(str(e))
        logger.error(traceback.format_exc())
    if 'type' in request.args and request.args['type'] == 'json':
        return jsonify(configs)
    else:
        return render_template('group/index.html', res=configs)


@mod.route("/add", methods=['GET'])
def group_add_get():
    return render_template('group/add.html')


@mod.route("/add", methods=['POST'])
def group_add():
    res = APIMixin().api_res
    name = str(request.form.get("name")).strip()
    desc = str(request.form.get("desc")).strip()
    if not name or not desc:
        msg = "参数不足"
        res["msg"] = msg
        res["code"] = 400
        return json.dumps(res)
    receivers = str(request.form.get("receivers"))
    callback_url = str(request.form.get("callback_url"))
    # default alerter
    alert_type = 0
    if receivers:
        receivers = receivers.strip().split(",")
        callback_url = None
    elif not callback_url:
        msg = "参数不合法"
        res["msg"] = msg
        res["code"] = 400
        return json.dumps(res)
    else:
        alert_type = 1
    try:
        res["data"] = config.co_config_group.add(name, desc, receivers, callback_url, alert_type)
    except Exception as e:
        logger.error(traceback.format_exc())
        msg = "Add group <name: %s> failed: <%s>" % (name, str(e))
        res["msg"] = msg
        res["code"] = 500
    return json.dumps(res)


@mod.route("/invalid", methods=['GET'])
def group_invalid():
    res = APIMixin().api_res
    if "name" in request.args and request.args["name"]:
        name = request.args["name"]
        logger.debug(name)
        if not config.co_config_group.exists(name):
            msg = "组数据不匹配"
            res["msg"] = msg
            res["code"] = 500
    else:
        msg = "参数不足"
        res["msg"] = msg
        res["code"] = 400
    try:
        config.co_config_group.invalid(name)
    except Exception as e:
        logger.error(traceback.format_exc())
        msg = "Invalid group <name: %s> failed: <%s>" % (name, str(e))
        res["msg"] = msg
        res["code"] = 500
    logger.debug(res)
    return json.dumps(res)


@mod.route("/update", methods=['GET'])
def group_update_get():
    res = APIMixin().api_res
    name = request.args.get("name", None)
    if not name or not config.co_config_group.exists(name):
        msg = "参数非法"
        res["msg"] = msg
        res["code"] = 400
    else:
        config_item = config.co_config_group.get(name)
        res["data"] = config_item
    logger.debug(res)
    return json.dumps(res)


@mod.route("/update", methods=['POST'])
def group_update():
    res = APIMixin().api_res
    try:
        name = str(request.values.get("name"))
        if not name or not config.co_config_group.exists(name):
            msg = "Config group name <%s> not existed" % name
            res["msg"] = msg
            res["code"] = 400
        else:
            update_dic = dict()
            update_dic["desc"] = str(request.values.get("desc"))
            receivers = str(request.values.get("receivers"))
            update_dic["receivers"] = receivers.strip().split(",")
            update_dic["callback_url"] = str(request.values.get("callback_url"))
            logger.debug(update_dic)
            config.co_config_group.update_one({"name": name}, update_dic)
    except Exception as e:
        msg = "Update config <%s> failed: <%s>" % (name, str(e))
        res["msg"] = msg
        res["code"] = 500
    return json.dumps(res)
