# -*- coding: utf-8 -*-
import os
from utils.mongo import MongoConn
from db import CoConfig, CoConfigGroup, CoDetail, CoScanner, CoAlerter

_basedir = os.path.abspath(os.path.dirname(__file__))

# db config
MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_NAME = 'easy_http'

REDIS_HOST = '127.0.0.1'
REDIS_HOST = 6379
mdb = MongoConn(MONGODB_HOST, db_name=MONGODB_NAME)

class Config:
    LOG_FOLDER = os.path.join(os.environ['HOME']+'/var/easy_http/', 'logs')
    
    MAIL_SENDER = 'lizhenxiang@pjlab.org.cn'
    SMS_DEFAULT_TO_LIST = [
        "lizhenxiang@pjlab.org.cn",
    ]

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    # ms
    MAX_REQUEST_TIMEOUT = 2000
    # s
    HTTP_SCANNER_INTERVAL = 5
    # s
    ALERTER_INTERVAL = 10
    # s
    DEFAULT_SCANNER_SECONDS = 10

    LATEST_NUM = 3

    HTTP_OK_CODE = 200
    UNKNOWN_SERVER_CODE = -100

    def __init__(self):
        pass

    @staticmethod
    def init_app():
        pass


class DevelopConfig(Config):
    DEBUG_MODE = True
    APP_PORT = 9481

    def __init__(self):
        self.co_config = CoConfig(mdb)
        self.co_detail = CoDetail(mdb)
        self.co_config_group = CoConfigGroup(mdb)
        self.co_scanner = CoScanner(mdb)
        self.co_alerter = CoAlerter(mdb)


class ProdConfig(Config):
    DEBUG_MODE = False
    APP_PORT = 9482

    # db config
    def __init__(self):
        self.co_config = CoConfig(mdb)
        self.co_detail = CoDetail(mdb)
        self.co_config_group = CoConfigGroup(mdb)
        self.co_scanner = CoScanner(mdb)
        self.co_alerter = CoAlerter(mdb)


def load_config():
    """load config class"""
    mode = os.environ.get('MODE')
    try:
        if mode == 'PROD':
            return ProdConfig()
        elif mode == 'DEVELOP':
            return DevelopConfig()
        else:
            return DevelopConfig()
    except ImportError as e:
        return None
