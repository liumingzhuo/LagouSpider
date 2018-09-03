import threading
import time

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

conn = MongoClient('127.0.0.1', 27017)
db = conn.lagou

proxy = {"https": 'https://%s' % input('请输入代理IP: ')}

def get_json(keyword, page):
    data = {
        'pn': page,
        'kd': keyword,
    }
    url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E6%88%90%E9%83%BD&needAddtionalResult=false'
    headers = {
        'Accept':           'application/json, text/javascript, */*; q=0.01',
        'Content-Type':     'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin':           'https://www.lagou.com',
        'Referer':          'https://www.lagou.com/jobs/list_{}?city=%E6%88%90%E9%83%BD&cl=false'
                            '&fromSearch=true&labelWords=&suginput='.format(keyword),
        'User-Agent':       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie':           '_ga=GA1.2.1176219052.1525516654; user_trace_token=20180505183734-522d0969-5050-11e8-8032-5254005c3644; LGUID=20180505183734-522d0d7e-5050-11e8-8032-5254005c3644; index_location_city=%E6%88%90%E9%83%BD; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; _gid=GA1.2.1609482079.1535252885; JSESSIONID=ABAAABAAAGFABEFAF1B82E55AD78E727FBE8F9A524F11DC; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1535252885,1535388327,1535567308,1535581083; X_HTTP_TOKEN=0a538ca6731db75799ffed14888c0323; LG_LOGIN_USER_ID=1e8c26fb6976688aebb8f4404658cbe533c7012a4bb16eae; _putrc=68BFC909BD7605C8; login=true; unick=%E9%BB%84%E7%A7%91; hasDeliver=138; gate_login_token=9ceb36e4bc23b9210272f2e4722a69b28adc98a79698db16; LGSID=20180831132504-3714cdf5-acde-11e8-be60-525400f775ce; TG-TRACK-CODE=jobs_again; _gat=1; SEARCH_ID=2fa0ee6acb5b4235b444caff55887def; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1535697322; LGRID=20180831143522-09678973-ace8-11e8-be67-525400f775ce'
    }

    try:
        # r = requests.post(url, headers=headers, data=data, proxies=proxy, timeout=10)
        r = requests.post(url, headers=headers, data=data, timeout=10)
        if r.status_code == 200:
            print(r.json())
            return r.json()
        else:
            print('crawl page %s failed' % page)
    except Exception as e:
        print(e)
        return

def parse_jd_page(_id):
    url = 'https://www.lagou.com/jobs/%s.html' % _id
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/68.0.3440.106 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers)
        html = r.text.replace('<br>', '')
        soup = BeautifulSoup(html, 'lxml')
        jd = soup.find('dd', class_='job_bt').get_text()
        addr = soup.find('dd', class_='job-address').get_text()
        addr = ''.join(addr.split())
        return jd, addr
    except Exception:
        return None, None

def parse_json(data):
    if data:
        try:
            results = data.get('content').get('positionResult').get('result')
            for result in results:
                lagou = {}
                lagou['_id'] = result.get('positionId')
                lagou['postion_id'] = result.get('positionId')
                lagou['城市'] = result.get('city')
                lagou['公司名字'] = result.get('companyFullName')
                lagou['公司福利'] = result.get('companyLabelList')
                lagou['Logo'] = result.get('companyLogo')
                lagou['公司简称'] = result.get('companyShortName')
                lagou['公司大小'] = result.get('companySize')
                lagou['发布时间'] = result.get('createTime')
                lagou['区域'] = result.get('district')
                lagou['学历限制'] = result.get('education')
                lagou['融资'] = result.get('financeStage')
                lagou['职位类型'] = result.get('firstType')
                lagou['行业类型'] = result.get('industryField')
                lagou['职位'] = result.get('jobNature')
                lagou['职位优势'] = result.get('positionAdvantage')
                lagou['职位名'] = result.get('positionName')
                lagou['薪酬水平'] = result.get('salary')
                lagou['职位类别'] = result.get('secondType')
                lagou['地铁站'] = result.get('stationname')
                lagou['地铁线'] = result.get('subwayline')
                lagou['工作经验'] = result.get('workYear')
                # lagou['任职要求'], lagou['工作地点'] = parse_jd_page(result.get('positionId'))
                yield lagou
        except ValueError as e:
            print(e)
            return
    else:
        return None

def save_to_mongo(data):
    if data:
        for d in data:
            job.insert(d)
            print('正在保存 %s 至mongodb' % d)
    else:
        return None

def main(keyword, page):
    data = get_json(keyword, page)
    parse_jd_page(data)
    data_gne = parse_json(data)
    save_to_mongo(data_gne)

if __name__ == '__main__':
    keyword = input('要爬取的职位: ')
    pages = int(input('要爬取的页数: '))
    job = db[keyword + '_threadings']

    t1 = time.time()

    threads = []
    for i in range(1, pages + 1):
        t = threading.Thread(target=main, args=(keyword, i))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    t2 = time.time()

    print('多线线程版耗时%s秒' % (t2 - t1))
