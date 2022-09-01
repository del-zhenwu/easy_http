# -*- coding: utf-8 -*-
import copy
import traceback
import logging
from application import app_config as config
from agent.http import HttpPlugin
from utils.decorator import time_wrapper

logger = logging.getLogger('easy_http.agent.collect')


@time_wrapper
def collect_http_stats(http_config):
    """
    :param http_config:监控项HTTP配置信息：
        {app_name, domain, url, method, headers, params, asserts, timeout}
    :return: res: Boolean
    """
    res = True
    try:
        mp = HttpPlugin(http_config)
        doc = config.co_detail.init_doc(http_config)
        mp.start()
        mp.join()
        mp.stop()
        doc["code"] = mp.stats["code"]
        doc["msg"] = mp.stats["msg"]
        doc["content"] = mp.stats["content"]
        config.co_detail.add(doc)
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())
        res = False
    finally:
        return res


if __name__ == "__main__":
    collect_http_stats()
