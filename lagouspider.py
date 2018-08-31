from time import sleep

import requests
from bs4 import BeautifulSoup
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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/68.0.3440.106 Safari/537.36',
        'Accept':     'application/json, text/javascript, */*; q=0.01',
        'Referer':    'https://www.lagou.com/jobs/list_{}?city=%E6%88%90%E9%83%BD&cl=false&fromSearch=true&labe'
                      'lWords=&suginput='.format(keyword)}
    try:
        r = requests.post(url, headers=headers, data=data)
        return r.json()
    except Exception as e:
        print(e)

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
        results = data.get('content').get('positionResult').get('result')
        for result in results:
            lagou = {}
            lagou['_id'] = result.get("companyFullName") + ' - ' + result.get('positionName') + \
                           ' — ' + result.get('createTime')
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
            lagou['任职要求'], lagou['工作地点'] = parse_jd_page(result.get('positionId'))
            yield lagou
    else:
        return None

def save_to_mongo(data):
    if data:
        for d in data:
            job.insert(d)
            print('正在保存 %s 至mongodb' % d)
            sleep(1)
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
