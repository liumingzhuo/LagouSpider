#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 拉勾网全站爬虫 '''
import multiprocessing
import re
import threading
import time
from multiprocessing.pool import Pool

import redis
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# HOST = '192.168.31.214'
HOST = '127.0.0.1'
PORT = 6379
DELAY_TIME = 0.5

redis_conn = redis.Redis(host=HOST, port=6379, db=0)

mongo_conn = MongoClient(HOST, 27017, connect=False)
db = mongo_conn.lagou
job_curse = db.lagou_jobs
comp_curse = db.lagou_comps

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/68.0.3440.106 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Cookie': '_ga=GA1.2.1176219052.1525516654; user_trace_token=20180505183734-522d0969-5050-11e8-8032-5254005c3644; LGUID=20180505183734-522d0d7e-5050-11e8-8032-5254005c3644; index_location_city=%E6%88%90%E9%83%BD; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; _gid=GA1.2.1609482079.1535252885; JSESSIONID=ABAAABAAAGFABEFAF1B82E55AD78E727FBE8F9A524F11DC; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1535252885,1535388327,1535567308,1535581083; X_HTTP_TOKEN=0a538ca6731db75799ffed14888c0323; LG_LOGIN_USER_ID=1e8c26fb6976688aebb8f4404658cbe533c7012a4bb16eae; _putrc=68BFC909BD7605C8; login=true; unick=%E9%BB%84%E7%A7%91; hasDeliver=138; gate_login_token=9ceb36e4bc23b9210272f2e4722a69b28adc98a79698db16; LGSID=20180831132504-3714cdf5-acde-11e8-be60-525400f775ce; TG-TRACK-CODE=jobs_again; _gat=1; SEARCH_ID=2fa0ee6acb5b4235b444caff55887def; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1535697322; LGRID=20180831143522-09678973-ace8-11e8-be67-525400f775ce'
}


def crawler_links(url, retry_num=2, charset='utf-8'):
    '''
    爬取新的带有lagou标签的url
    '''
    print('正在爬通用信息 %s' % url)
    try:
        r = requests.get(url, headers=headers, timeout=10, )
        if r.status_code == 200:
            redis_conn.sadd('crawled_common', url)
            redis_conn.sadd('crawled_urls', url)

            # cs = r.encoding
            # if not cs:
            #     cs = charset
            # html = r.content.decode(cs)

            html = r.text
            urls = parse_urls(html)
            for _url in urls:
                if not redis_conn.sismember('crawled_urls', _url):
                    redis_conn.sadd('un_crawled_urls', _url)
                else:
                    continue
        elif r.status_code == 301 or r.status_code == 404:
            redis_conn.sadd('bad_urls', url)
        else:
            redis_conn.sadd('un_crawled_urls', url)
            print('crawl爬虫出错 %s, status code %s' % (url, r.status_code))
    except Exception as e:
        print(e)
        if retry_num > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return crawler_links(url, retry_num - 1)
        return


def crawl_position(url, retry_num=3):
    '''
    爬取职位信息
    '''
    print('正在爬取职位 %s' % url)
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            redis_conn.sadd('crawled_position', url)
            redis_conn.sadd('crawled_urls', url)
            html = r.text
            data = parse_position(html)
            save_to_mongo(data)
        elif r.status_code == 301 or r.status_code == 404:
            redis_conn.sadd('bad_urls', url)

            print('crawl position %s failed, status code %s' % (url, r.status_code))
        else:
            redis_conn.sadd('un_crawled_urls', url)
    except Exception as e:
        print(e)
        if retry_num > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return crawl_position(url, retry_num - 1)
        return None


def crawl_company(url):
    print('正在爬公司信息 %s' % url)
    redis_conn.sadd('crawled_company', url)
    redis_conn.sadd('crawled_urls', url)
    return None

    # TODO 公司信息先不抓取，后续再说
    # try:
    #     r = requests.get(url, headers=headers, timeout=10)
    #     if r.status_code == 200:
    #         redis_conn.sadd('crawled_urls', url)
    #         pass
    #         # infos = parse_company(html)
    #     else:
    #         print('crawl company %s failed, status code %s' % (url, r.status_code))
    # except Exception as e:
    #     print(e)
    #     return


def parse_urls(url):
    '''
    解析所有带有lagou标签的url
    '''
    try:
        url_pattern = re.compile('href="(https://.*?lagou.*?)"')
        urls = re.findall(url_pattern, url)
        return urls
    except Exception as e:
        print(e)
        return None


def is_postion_url(url):
    '''
    判断url是不是职位页面url
    '''
    job_pattern = re.compile('https://www.lagou.com/jobs/\d+?.html')
    found = re.search(job_pattern, url)
    return bool(found)


def is_company_url(url):
    '''
    判断url是不是公司页面url
    '''
    cmp_pattern = re.compile('https://www.lagou.com/gongsi/\d+?.html')
    found = re.search(cmp_pattern, url)
    return bool(found)


def parse_position(html):
    '''
    使用bs提取职位页面所有需要的信息
    '''
    if html:
        try:
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
        except Exception as e:
            print('解析规则有变化 %s' % e)
            return None
    else:
        return None


def parse_company(html):
    # to be done
    pass


def save_to_mongo(data):
    '''
    将提取出的信息保存到mongodb
    '''
    if data:
        try:
            job_curse.insert(data)
            print('正在保存 %s 至mongodb' % data)
        except Exception as e:
            print(e)
            return None
    else:
        return None


def main():
    ''' 主函数 '''

    print('去吧！皮卡丘')

    lock.acquire()
    if redis_conn.scard('un_crawled_urls') > 0:
        start_url = redis_conn.spop('un_crawled_urls').decode('utf-8')
    else:
        start_url = 'https://www.lagou.com/'
    redis_conn.sadd('un_crawled_urls', start_url)
    lock.release()

    # 对url进行判断，分别爬取
    while redis_conn.scard('un_crawled_urls') > 0:
        time.sleep(1)
        url = redis_conn.spop('un_crawled_urls').decode('utf-8')
        if is_postion_url(url):
            crawl_position(url)
        elif is_company_url(url):
            crawl_company(url)
        else:
            crawler_links(url)


if __name__ == '__main__':
    t1 = time.time()
    lock = threading.Lock()
    for i in range(60):
        t = threading.Thread(target=main, args=())
        t.start()
    t.join()

    t2 = time.time()

    print("本次爬取用时%s秒" % (t2 - t1))

    # cores = multiprocessing.cpu_count()
    # pool = Pool(processes=cores)
    #
    # for i in range(cores):
    #     pool.apply_async(main, args=())  # 维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
    # pool.close()
    # pool.join()
