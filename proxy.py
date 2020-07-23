import re
import time
import os
import logging
import requests
import chardet
import execjs
from datetime import datetime
from utils import get_headers
from lxml import etree
from lxml.html import fromstring
from config import *

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__ParseFunc__'] = []
        for k, v in attrs.items():
            if 'parse_' in k:
                attrs['__ParseFunc__'].append(k)
                count += 1
        attrs['__ParseFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Extractor(object, metaclass=ProxyMetaclass):

    def get_proxies(self, callback):
        proxy_list = []
        for proxy in eval("self.{}()".format(callback)):
            proxy_list.append(proxy)
        return proxy_list

    def get_js_func(self, txt):
        return re.search(r'eval\((.*)\)', txt).group(1)

    def get_port_exp(self, exp_str):
        return re.search(r'(?<=font>"\+)(.*)(?=\))', exp_str).group(1)

    def get_page(self, url, proxies=None):
        logging.info(f'开始爬取 {url}')
        retry = 1
        while(True):
            try:
                r = requests.get(url, headers=get_headers(),
                                 proxies=proxies, timeout=8)
                # r.encoding = chardet.detect(r.content)['encoding']
                logging.info(f'{r.status_code} {url} {r.encoding}')
                if r.status_code == 200:
                    return r.text
                else:
                    raise ConnectionError
            except Exception as e:
                retry += 1
                print(e)
                logging.info(f'{url}请求失败，等待3s重新尝试第{retry}次')
                time.sleep(3)
            if retry == 4:
                logging.info(f'已重试{retry}次，跳过')
                break

    def parse_kuaidaili(self, page_count=6):
        start_url = 'https://www.kuaidaili.com/free/inha/{}/'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        proxy_list = []
        for url in urls:
            page_content = self.get_page(url)
            trs = re.findall(r'<tr>(.*?)</tr>', page_content, re.S)
            for tr in trs[1:]:
                ip = re.findall(r'="IP">(.*?)</td>', tr)[0]
                port = re.findall(r'="PORT">(.*?)</td>', tr)[0]
                scheme = re.findall(r'="类型">(.*?)</td>', tr)[0].lower()
                proxy = {'proxy': scheme + '://' + ip + ':' + port}
                proxy_list.append(proxy)
        return proxy_list

    def parse_89ip(self, page_count=6):
        start_url = 'http://www.89ip.cn/index_{}.html'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        proxy_list = []
        for url in urls:
            page_content = self.get_page(url)
            page = etree.HTML(page_content)
            trs = page.xpath('//tbody/tr')
            for tr in trs:
                ip = tr.xpath('./td[1]/text()')[0].strip()
                port = tr.xpath('./td[2]/text()')[0].strip()
                proxy = {'proxy': 'http://' + ip + ':' + port}
                proxy_list.append(proxy)
        return proxy_list

    def parse_ip3366(self, page_count=1):
        start_url = 'http://www.ip3366.net/free/?stype=1&page={}'
        urls = [start_url.format(page) for page in range(1, page_count+1)]
        proxy_list = []
        for url in urls:
            page_content = self.get_page(url)
            page = etree.HTML(page_content)
            trs = page.xpath('//tbody/tr')
            for tr in trs:
                ip = tr.xpath('./td[1]/text()')[0]
                port = tr.xpath('./td[2]/text()')[0]
                scheme = tr.xpath('./td[4]/text()')[0].lower()
                proxy = {'proxy': scheme + '://' + ip + ':' + port}
                proxy_list.append(proxy)
        return proxy_list

    def parse_xila(self, page_count=2):
        start_url = 'http://www.xiladaili.com/gaoni/{}/'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        proxy_list = []
        for url in urls:
            page_content = self.get_page(url)
            if not page_content:
                return []
            page = etree.HTML(page_content)
            trs = page.xpath('//tbody/tr')
            for tr in trs:
                ip_port = tr.xpath('./td[1]/text()')[0]
                scheme = tr.xpath(
                    './td[2]/text()')[0].replace('代理', '').split(',')[0].lower()

                proxy = {
                    'proxy': scheme + '://' + ip_port
                }
                proxy_list.append(proxy)
        return proxy_list

    def parse_spys(self):
        url = 'http://spys.one/free-proxy-list/CN/'
        proxies = {'http': 'http://127.0.0.1:7890',
                   'https': 'http://127.0.0.1:7890'}
        response = self.get_page(url, proxies=proxies)
        parser = fromstring(response)
        js_func = self.get_js_func(response)
        js_exp = execjs.eval(js_func)
        proxy_list = []
        trs = parser.xpath('//table[2]//table[@width="100%"]//tr')[3:-2]
        for tr in trs:
            if len(tr.xpath('./td[3]/font/text()')) > 0 and tr.xpath('./td[3]/font/text()')[0] != 'NOA':
                host = tr.xpath('./td[1]/font/text()')[0]
                scheme_str = ''.join(tr.xpath('./td[2]//text()')).lower()
                scheme = re.search(r'(http|https|socks5)\b',
                                   scheme_str).group(1)
                port_temp = tr.xpath('./td[1]/font/script/text()')[0]
                port_exp = self.get_port_exp(port_temp)
                port = execjs.compile(JS_PORT).call('a', js_exp, port_exp)
                proxy = scheme + '://' + host + ':' + port
                proxy = {
                    'proxy': proxy
                }
                proxy_list.append(proxy)
        return proxy_list

    # 失效
    # def parse_xici(self, page_count=3):
    #     start_url = 'http://www.xicidaili.com/nn/{}'
    #     urls = [start_url.format(page) for page in range(1, page_count + 1)]
    #     proxy_list = []
    #     for url in urls:
    #         page_content = self.get_page(url)
    #         if not page_content:
    #             return []
    #         page_html = etree.HTML(page_content)
    #         trs = page_html.xpath('//*[@id="ip_list"]/tr')  # ajax动态修改，没有tbody
    #         for tr in trs[1:]:
    #             ip = tr.xpath('./td[2]/text()')[0]
    #             port = tr.xpath('./td[3]/text()')[0]
    #             proxy = {'proxy': ip + ':' + port}
    #             proxy_list.append(proxy)
    #     return proxy_list
