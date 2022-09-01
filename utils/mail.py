# -*- coding: utf-8 -*-

from cmath import log
import logging
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from pyparsing import traceback
from requests import post
# from utils.http_client import HttpClient
from application import app_config as config

logger = logging.getLogger('easy_http.utils.mail')


def send_email(subject, content, receivers=None):
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header("Online http-service alert")
    # message['To'] = Header("HTTP Monitor")
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtp_obj = smtplib.SMTP('partner.outlook.cn', 25)
        smtp_obj.ehlo()
        smtp_obj.starttls()
        # TODO:
        smtp_obj.login('lizhenxiang@pjlab.org.cn', 'Lghlmcl-10000')
        logger.debug(receivers)
        if not receivers:
            receivers = config.SMS_DEFAULT_TO_LIST
        result = smtp_obj.sendmail(config.MAIL_SENDER, receivers, message.as_string())
        logger.debug(result)
        logger.debug("Send email to: %s" % receivers)
    except smtplib.SMTPException as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())


def send_email_sms(subject, content, receivers=None):
    pass


if __name__ == '__main__':
    send_email("[mail test]", "test")