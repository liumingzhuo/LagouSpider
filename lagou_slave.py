#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 拉勾网全站爬虫 slave节点'''
import multiprocessing
import re
import threading
import time
from multiprocessing.pool import Pool

import redis
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

from check import parse_checker

HOST = '192.168.31.214'
PORT = 6379
DELAY_TIME = 0.5

redis_pool = redis.ConnectionPool(host=HOST, port=PORT, max_connections=50)
redis_conn = redis.Redis(connection_pool=redis_pool)

mongo_conn = MongoClient(HOST, 27017, connect=False)
db = mongo_conn.lagou
job_curse = db.lagou_jobs
comp_curse = db.lagou_comps

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/68.0.3440.106 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Cookie': '_JSESSIONID=ABAAABAAAGFABEFCE8178836CE129D66902A4037694E69E; _ga=GA1.2.315798882.1536057004; _gid=GA1.2.564034052.1536057004; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1536057005; user_trace_token=20180904182759-32051efb-b02d-11e8-85bf-525400f775ce; LGUID=20180904182759-320521bd-b02d-11e8-85bf-525400f775ce; index_location_city=%E5%85%A8%E5%9B%BD; X_HTTP_TOKEN=c56567765dd9e74a4dcecf36d6aebf19; LG_LOGIN_USER_ID=62014dee7e0768db6652e8d72a25508483f86729554ae4ba; _putrc=68BFC909BD7605C8; login=true; unick=%E9%BB%84%E7%A7%91; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=138; SEARCH_ID=575835590d42453b9bc2cf0fff35bee6; gate_login_token=d7792e76460db048715dbfc5bca5a6d34a0b523468a72f3d; LGSID=20180904214250-6a618153-b048-11e8-b4e7-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; TG-TRACK-CODE=index_recjob; _gat=1; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1536069970; LGRID=20180904220404-61c396e2-b04b-11e8-85c9-525400f775ce'
}


def crawl_position(url, retry_num=3):
    '''
    爬取职位信息
    '''
    print('正在爬取职位 %s' % url)
    try:
        r = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(e)
        if retry_num > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return crawl_position(url, retry_num - 1)
        return None

    if r.status_code == 200:
        html = r.text
        data = parse_position(html)
        save_to_mongo(url, data)
    elif r.status_code == 301 or r.status_code == 404:
        redis_conn.sadd('bad_urls', url)

        print('crawl position %s failed, status code %s' % (url, r.status_code))
    else:
        redis_conn.sadd('un_crawled_urls', url)


def parse_position(html):
    '''
    使用bs提取职位页面所有需要的信息
    '''
    if html:

        parse_checker(html)
        # anspider_checker(html)

        soup = BeautifulSoup(html, 'lxml')
        job_name = soup.select_one(".job-name .name").string
        depart_name = soup.select_one(".company").string
        city = soup.select(".job_request span")[1].string.strip('/').strip()
        experience = soup.select(".job_request span")[2].string.strip('/').strip()
        edu = soup.select(".job_request span")[3].string.strip('/').strip()
        work_time = soup.select(".job_request span")[4].string.strip('/').strip()
        advantage = soup.select_one(".job-advantage p").string
        job_desc = soup.select_one(".job_bt").text
        addr = ''.join(soup.select_one(".work_addr").text.split()[:-1])

        company = soup.select_one(".job_company h2").text.split()[0]
        comp_field = soup.select(".c_feature li")[0].text.split()
        progress = soup.select(".c_feature li")[1].text.split()[0]
        scale = soup.select(".c_feature li")[2].text.split()[0]
        comp_url = soup.select(".c_feature li")[3].text.split()[0]

        job_data = dict(
            job_name=job_name,
            depart_name=depart_name,
            city=city,
            experience=experience,
            edu=edu,
            work_time=work_time,
            advantage=advantage,
            job_desc=job_desc,
            addr=addr,
            company=company,
            comp_field=comp_field,
            progress=progress,
            scale=scale,
            comp_url=comp_url,
        )
        return job_data


    else:
        return None


def save_to_mongo(url, data):
    '''
    将提取出的信息保存到mongodb
    '''
    if data:
        try:
            job_curse.insert(data)
            print('正在保存 %s 至mongodb' % data)
            redis_conn.sadd('crawled_position', url)
            redis_conn.sadd('crawled_urls', url)
        except Exception as e:
            print(e)
            return None
    else:
        return None


def main():
    ''' 主函数 '''

    print('去吧！皮卡丘')
    print('待爬队列长度', redis_conn.scard('un_crawled_urls'))

    # 对url进行判断，分别爬取
    while redis_conn.scard('position_urls') > 0:
        time.sleep(1)
        lock.acquire()
        url = redis_conn.spop('position_urls').decode('utf-8')
        lock.release()
        crawl_position(url)


if __name__ == '__main__':
    t1 = time.time()
    lock = threading.Lock()
    for i in range(1):
        t = threading.Thread(target=main, args=())
        t.start()
    t.join()

    t2 = time.time()

    print("本次爬取用时%s秒" % (t2 - t1))
