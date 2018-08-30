from time import sleep

import requests
from pymongo import MongoClient

conn = MongoClient('127.0.0.1', 27017)
db = conn.lagou

def get_json(keyword, page):
    data = {
        'pn': page,
        'kd': keyword,
    }
    url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E6%88%90%E9%83%BD&needAddtionalResult=false'
    headers = {
        'POST':               '/jobs/positionAjax.json?city=%E6%88%90%E9%83%BD&needAddtionalResult=false HTTP/1.1',
        'Host':               'www.lagou.com',
        'Connection':         'keep-alive',
        'Content-Length':     '25',
        'Origin':             'https://www.lagou.com',
        'X-Anit-Forge-Code':  '0',
        'User-Agent':         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/68.0.3440.106 Safari/537.36',
        'Content-Type':       'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept':             'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With':   'XMLHttpRequest',
        'X-Anit-Forge-Token': 'None',
        'Referer':            'https://www.lagou.com/jobs/list_{}?city=%E6%88%90%E9%83%BD&cl=false&fromSearch=true&labe'
                              'lWords=&suginput='.format(keyword),
        'Accept-Encoding':    'gzip, deflate, br',
        'Accept-Language':    'zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cookie':             '_ga=GA1.2.1176219052.1525516654; user_trace_token=20180505183734-522d0969-5050-11e8-8032'
                              '-5254005c3644; LGUID=20180505183734-522d0d7e-5050-11e8-8032-5254005c3644; index_location'
                              '_city=%E6%88%90%E9%83%BD; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPub'
                              'lish=1; LG_LOGIN_USER_ID=dd839b05c99bff21d886dafddcade0c75f7637bcc62921fd; _gid=GA1.2.16'
                              '09482079.1535252885; hasDeliver=138; JSESSIONID=ABAAABAAAGFABEFAF1B82E55AD78E727FBE8F9A5'
                              '24F11DC; LGSID=20180830061802-650aab23-abd9-11e8-b30a-5254005c3644; Hm_lvt_4233e74dff0ae'
                              '5bd0a3d81c6ccf756e6=1535252885,1535388327,1535567308,1535581083; _putrc=68BFC909BD7605C8'
                              '; login=true; unick=%E9%BB%84%E7%A7%91; gate_login_token=c132653baa4f5ffe5cd805cd4879f62'
                              '9e91846aec42d7f18; TG-TRACK-CODE=search_code; _gat=1; Hm_lpvt_4233e74dff0ae5bd0a3d81c6cc'
                              'f756e6=1535587056; LGRID=20180830075736-4dbcf2ed-abe7-11e8-b30a-5254005c3644; SEARCH_ID'
                              '=3534762e47954b9cb9a3d7fd423771fb'}
    try:
        r = requests.post(url, headers=headers, data=data)
        return r.json()
    except Exception as e:
        print(e)

def parse_json(data):
    if data:
        results = data.get('content').get('positionResult').get('result')
        for result in results:
            lagou = {}
            lagou['_id'] = result.get("companyFullName") + ' - ' + result.get('positionName') + \
                           ' — ' + result.get('createTime')
            lagou['city'] = result.get('city')
            lagou['businessZones'] = result.get('businessZones')
            lagou['companyFullName'] = result.get('companyFullName')
            lagou['companyLabelList'] = result.get('companyLabelList')
            lagou['companyLogo'] = result.get('companyLogo')
            lagou['companyShortName'] = result.get('companyShortName')
            lagou['companySize'] = result.get('companySize')
            lagou['createTime'] = result.get('createTime')
            lagou['district'] = result.get('district')
            lagou['education'] = result.get('education')
            lagou['financeStage'] = result.get('financeStage')
            lagou['firstType'] = result.get('firstType')
            lagou['hitags'] = result.get('hitags')
            lagou['industryField'] = result.get('industryField')
            lagou['jobNature'] = result.get('jobNature')
            lagou['linestaion'] = result.get('linestaion')
            lagou['positionAdvantage'] = result.get('positionAdvantage')
            lagou['positionLables'] = result.get('positionLables')
            lagou['positionName'] = result.get('positionName')
            lagou['salary'] = result.get('salary')
            lagou['secondType'] = result.get('secondType')
            lagou['stationname'] = result.get('stationname')
            lagou['subwayline'] = result.get('subwayline')
            lagou['workYear'] = result.get('workYear')
            print('数据解析完成准备保存', lagou)
            yield lagou
    else:
        return None

def save_to_mongo(data):
    if data:
        for d in data:
            job.insert(d)
            print('正在保存 %s 至mongodb' % d)
    else:
        return None

def main(keyword, pages):
    for i in range(1, pages + 1):
        data = get_json(keyword, i)
        data_gne = parse_json(data)
        save_to_mongo(data_gne)
        sleep(10)

if __name__ == '__main__':
    keyword = input('要爬取的职位: ')
    pages = int(input('要爬取的页数: '))
    job = db.python_job
    main(keyword, pages)
