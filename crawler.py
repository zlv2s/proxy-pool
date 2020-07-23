import time
import logging
from proxy import Extractor
from validate import Validate
from mongo_db import MongoDB


def check():
    '''
    定时检测数据库中代理的可用性
    :return:
    '''
    while True:
        m = MongoDB()
        count = m.get_count()
        if not count == 0:
            logging.info('开始检测数据库中代理可用性>>>>>>>>')
            proxies = m.get(count)
            Validate().valid_many(proxies, 'check')
        time.sleep(10 * 60)


class Crawler(object):

    def __init__(self):
        self.crawler = Extractor()

    def start(self):
        for callback_label in range(self.crawler.__ParseFuncCount__):
            callback = self.crawler.__ParseFunc__[callback_label]
            # 获取代理
            proxy_list = self.crawler.get_proxies(callback)
            # 验证可用性
            Validate().valid_many(proxy_list, 'insert')


def crawl_ip():
    while True:
        logging.info('开始抓取可用的代理IP>>>>>>>>>>')
        Crawler().start()
        time.sleep(2 * 60 * 60)
