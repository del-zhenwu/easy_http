from cmath import log
from json import load
import logging
# import redis
from bson.objectid import ObjectId
from utils.mongo import Collection
from utils import timer

logger = logging.getLogger('easy_http.db')


class CoConfig(Collection):
    def __init__(self, mdb):
        super(CoConfig, self).__init__(mdb, "co_config")

    def get(self, config_id):
        return self.find_one(query={"_id": config_id})

    def get_ids(self, all=True):
        configs = self.get_all(all=all)
        return [config["_id"] for config in configs]

    def get_all(self, all=True):
        if all is True:
            return self.find()
        return self.find(query={"state": 1})

    def get_groups(self):
        groups = []
        configs = self.get_all()
        for config_item in configs: 
            if "group" in config_item and config_item["group"] not in groups:
                groups.append(config_item["group"])
        logger.debug(groups)
        return groups

    def juhe(self):
        res = {}
        configs = self.get_all(all=False)
        for config_item in configs:
            group = str(config_item["group"])
            app_name = str(config_item["app_name"])
            if group in res:
                if app_name in res[group]:
                    res[group][app_name].append(config_item)
                else:
                    res[group].update({app_name: [config_item]})
            else:
                res[group] = {app_name: []}
                res[group][app_name].append(config_item)
        logger.debug(res)
        return res

    def update(self, config_id, data):
        pass


class CoDetail(Collection):
    def __init__(self, mdb):
        super(CoDetail, self).__init__(mdb, "co_detail")

    def add(self, doc):
        self.insert_one(doc)

    def init_doc(self, http_config):
        detail_doc = {
            "config_id": http_config["_id"],
            "app_name": http_config["app_name"],
            "domain": http_config["domain"],
            "url": http_config["url"],
            "content": {},
            "c_time": timer.get_current_time()
        }
        return detail_doc


class CoConfigGroup(Collection):
    def __init__(self, mdb):
        super(CoConfigGroup, self).__init__(mdb, "co_config_group")

    def add(self, name, desc, receivers, callback_url, alert_type):
        doc = self.new_doc_object()
        doc.update({
            "group_id": doc["_id"],
            "name": name,
            "desc": "" if not desc else desc,
            "receivers": receivers,
            "callback_url": callback_url,
            "alert_type": alert_type,
            "state": 1
        })
        logger.debug(doc)
        self.insert_one(doc)
        return doc["_id"]

    def get(self, group_name):
        return self.find_one(query={"name": group_name, "state": 1})

    def invalid(self, group_name):
        return self.update_one({"name": group_name}, {"state": 0})

    def set_receivers(self, group_name, receivers):
        return self.update_one({"name": group_name}, {"receivers": receivers})

    def get_all(self, all=True):
        if all is True:
            return self.find()
        return self.find(query={"state": 1})

    def exists(self, name):
        res = False
        doc = self.find_one({'name': name})
        if doc is not None:
            res = True
        return res


class CoScanner(Collection):
    def __init__(self, mdb):
        super(CoScanner, self).__init__(mdb, "scanner_job")


class CoAlerter(Collection):
    def __init__(self, mdb):
        super(CoAlerter, self).__init__(mdb, "alerter_job")
