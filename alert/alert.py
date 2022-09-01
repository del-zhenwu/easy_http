# -*- coding: utf-8 -*-
from cmath import log
import sys
import logging
from pymongo import DESCENDING
from utils import mail
from application import app_config as config
from utils.decorator import time_wrapper

logger = logging.getLogger('easy_http.alert.alert')


@time_wrapper
def do_alert(http_config):
    """
    get latest three detail with the given config
    :param http_config:
    :return:
    """
    msgs = ""
    http_status_flag = 0
    receivers = http_config["receivers"]
    config_id = http_config["_id"]
    app_name = http_config["app_name"]
    group = http_config["group"]
    latest = config.co_detail.find(query={"config_id": config_id}, sort=[("c_time", DESCENDING)], limit=config.LATEST_NUM)
    if latest and len(latest) < 3:
        logger.warning("Latest num less than 3, config_id %s" % config_id)
        return

    assert_res_msg = ""
    assertions = config.co_config.get(config_id)["assertions"]
    for detail_item in latest:
        logger.debug(detail_item)
        code = detail_item["code"]
        # msg = detail_item["msg"]
        # content = detail_item["content"]
        logger.debug(code)
        if code == config.HTTP_OK_CODE:
            http_status_flag = 0
            if not assertions:
                logger.debug("No assertions")
                return
            assert_flag = 0
            # TODO: 完善assertions
            for assert_item in assertions:
                comp_key = assert_item["assert_key"]
                comp = assert_item["assert_comparison"]
                comp_value = assert_item["assert_value"]
                if comp == "1":
                    logger.debug("start comparing")
                    if "content" in detail_item and comp_key in detail_item["content"] and detail_item["content"][comp_key] == comp_value:
                        break
                    else:
                        assert_flag = 1
            if assert_flag:
                if "content" in detail_item and comp_key in detail_item["content"]:
                    assert_res_msg = "<div>%s 预期返回：%s，实际返回：%s</div>" % (comp_key, comp_value, detail_item["content"][comp_key])
                else:
                    assert_res_msg = "<div>%s 不存在于预期返回中</div>" % comp_key
            break
        else:
            http_status_flag = 1
    logger.debug(http_status_flag)
    detail = ""
    if http_status_flag:
        detail = "<div>http响应问题：%s</div>" % detail_item["msg"]
    elif assert_res_msg:
        detail = assert_res_msg
    if detail:
        subject = "[%s - %s 报警]" % (group, app_name)
        msgs = "<h3>"+subject+"</h3>" + "<div><b>url: <a>%s</a><b></div>" % (http_config["domain"]+http_config["url"])
        logger.debug("Send email")
        mail.send_email(subject, msgs+detail, receivers=receivers)
