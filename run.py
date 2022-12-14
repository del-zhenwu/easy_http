# -*- coding: utf-8 -*-
import os
import logging
import argparse
import time
from logging import handlers
from application import create_app, socketio
from schedule.schedule import SchedulerWrapper
from db import CoConfig
from config import mdb

logger = logging.getLogger('easy_http')
app_instance = create_app()


formatter = logging.Formatter('[%(asctime)s] [%(levelname)-4s] [%(pathname)s:%(lineno)d] %(message)s')
if not os.path.exists(app_instance.config['LOG_FOLDER']):
    os.system('mkdir -p %s' % app_instance.config['LOG_FOLDER'])
fileTimeHandler = handlers.TimedRotatingFileHandler(os.path.join(app_instance.config['LOG_FOLDER'], 'easy_http'), "D", 1, 10)
fileTimeHandler.suffix = "%Y%m%d.log"
fileTimeHandler.setFormatter(formatter)
logging.basicConfig(level=logging.DEBUG)
fileTimeHandler.setFormatter(formatter)
logger.addHandler(fileTimeHandler)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-s", "--scanner", action="store_true")
group.add_argument("-a", "--alerter", action="store_true")
group.add_argument("-w", "--web_server", action="store_true")
args = parser.parse_args()


def write_pid(start_type):
    if os.path.exists('bin/%s.pid' % start_type):
        logger.error('Pid file existed')
        return False
    pid = os.getpid()
    with open('bin/%s.pid' % start_type, 'w') as fd:
        fd.write(str(pid))
    fd.close()
    return pid


def read_pid(start_type):
    pid = None
    if not os.path.exists('bin/%s.pid' % start_type):
        logger.error('Pid file not existed')
        return pid
    with open('%s.pid' % start_type, 'r') as fd:
        pid = fd.readlines().strip()
    fd.close()
    return pid


configs = CoConfig(mdb).get_all(all=False)
ids = CoConfig(mdb).get_ids(all=False)

if args.scanner:
    # set start type
    scanner_or_server = 'scanner'
    fileTimeHandler = handlers.TimedRotatingFileHandler(os.path.join(app_instance.config['LOG_FOLDER'], scanner_or_server), "D", 1, 10)
    fileTimeHandler.suffix = "%Y%m%d.log"
    fileTimeHandler.setFormatter(formatter)
    logging.basicConfig(level=logging.DEBUG)
    fileTimeHandler.setFormatter(formatter)
    logger.addHandler(fileTimeHandler)
    write_pid(scanner_or_server)
    sw = SchedulerWrapper(scanner_or_server)
    logger.debug("Http scanner scheduler start")
    sw.start()
    # loop each app
    for item in configs:
        # app_name = item["app_name"]
        config_id = item["_id"]
        # remove the scanner jobs if existed
        sw.remove_job(config_id)
        # add the new scanner job
        job = sw.add_job(
            job_id=config_id,
            seconds=item["seconds"],
            http_config=item
        )
        logger.info('Waiting to exit')
    logger.debug(sw.get_jobs())
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(5)
            config_ids = CoConfig(mdb).get_ids(all=False)
            for tmp_id in config_ids:
                if tmp_id in ids:
                    break
                else:
                    config = CoConfig(mdb).get(tmp_id)
                    job = sw.add_job(
                        job_id=config["_id"],
                        seconds=config["seconds"],
                        http_config=config
                    )
                    logger.debug("Scanner job added.")
            logger.error(time.time())
            
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        logger.warning("Job exited")
        sw.shutdown()


elif args.alerter:
    scanner_or_server = 'alerter'
    fileTimeHandler = handlers.TimedRotatingFileHandler(os.path.join(app_instance.config['LOG_FOLDER'], scanner_or_server), "D", 1, 10)
    fileTimeHandler.suffix = "%Y%m%d.log"
    fileTimeHandler.setFormatter(formatter)
    logging.basicConfig(level=logging.DEBUG)
    fileTimeHandler.setFormatter(formatter)
    logger.addHandler(fileTimeHandler)
    write_pid(scanner_or_server)

    sw = SchedulerWrapper(scanner_or_server)
    logger.debug("Alerter job scheduler start")
    sw.start()
    for item in configs:
        config_id = item["_id"]
        # remove the alerter jobs if existed
        sw.remove_job(config_id)
        sw.add_job(
            job_id=config_id,
            seconds=app_instance.config["ALERTER_INTERVAL"],
            http_config=item
        )
        logger.info('Waiting to exit')
    logger.debug(sw.get_jobs())
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(app_instance.config["ALERTER_INTERVAL"])
            config_ids = CoConfig(mdb).get_ids(all=False)
            for tmp_id in config_ids:
                if tmp_id in ids:
                    break
                else:
                    config = CoConfig(mdb).get(tmp_id)
                    job = sw.add_job(
                        job_id=tmp_id,
                        seconds=app_instance.config["ALERTER_INTERVAL"],
                        http_config=config
                    )
            logger.error(time.time())
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        logger.warning("Job exited")
        sw.shutdown()

elif args.web_server:
    scanner_or_server = 'web_server'
    fileTimeHandler = handlers.TimedRotatingFileHandler(os.path.join(app_instance.config['LOG_FOLDER'], scanner_or_server), "D", 1, 10)
    fileTimeHandler.suffix = "%Y%m%d.log"
    fileTimeHandler.setFormatter(formatter)
    logging.basicConfig(level=logging.DEBUG)
    fileTimeHandler.setFormatter(formatter)
    logger.addHandler(fileTimeHandler)
    write_pid(scanner_or_server)

    logger.debug("Easy http server start")
    socketio.run(app_instance, host='0.0.0.0', port=app_instance.config["APP_PORT"], debug=app_instance.config["DEBUG_MODE"])

