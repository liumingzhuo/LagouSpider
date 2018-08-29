import requests, time, json, csv

def get_index_ajax(keys, page):
    try:
        print("程序开始运行....")
        kd = keys
        url1 = 'https://www.lagou.com/jobs/list_' + kd + '?city=%E5%85%A8%E5%9B%BD'
        print(url1)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        req = requests.get(url1, headers=headers)
        if req.status_code == 200:
            print("200")
            headers1 = {
                'Cookie':             '_ga=GA1.2.2078231306.1534313377; user_trace_token=20180815140928-c4cd528d-a051-11e8-a3a0-5254005c3644; LGUID=20180815140928-c4cd55f7-a051-11e8-a3a0-5254005c3644; index_location_city=%E5%85%A8%E5%9B%BD; WEBTJ-ID=20180822165220-16560d5acab42d-08a38f705b617a-47e1039-2073600-16560d5acac216; _gid=GA1.2.1508439733.1534927941; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1534313378,1534927941; LGSID=20180822165222-aef8b51f-a5e8-11e8-abfc-5254005c3644; PRE_UTM=m_cf_cpt_baidu_pc; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Fs%3Fie%3Dutf-8%26f%3D8%26rsv_bp%3D1%26rsv_idx%3D1%26tn%3Dbaidu%26wd%3D%25E6%258B%2589%25E5%258B%25BE%25E7%25BD%2591%26oq%3D%2525E5%252595%252586%2525E6%2525A0%252587%2525E7%2525BD%252591%26rsv_pq%3De04f5728000b271a%26rsv_t%3D0884hvSlNcchy29B7iSI1jqK2bSQING0HpojNJfxZotqfFk8mEI0Yb2KIh4%26rqlang%3Dcn%26rsv_enter%3D1%26rsv_sug3%3D10%26rsv_sug1%3D10%26rsv_sug7%3D100%26rsv_sug2%3D0%26inputT%3D1526%26rsv_sug4%3D1526; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Flp%2Fhtml%2Fcommon.html%3Futm_source%3Dm_cf_cpt_baidu_pc; X_HTTP_TOKEN=4d664d756588e5a294cb59225f4468f4; JSESSIONID=ABAAABAAAGGABCB4F617E29A275918627C0C3630CFB21D6; TG-TRACK-CODE=index_search; _gat=1; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1534929380; LGRID=20180822171621-08c6718d-a5ec-11e8-abfc-5254005c3644; SEARCH_ID=0c95c11afbad45d2a31c6b71f321c6ff',
                'DNT':                '1',
                'Host':               'www.lagou.com',
                'Origin':             'https://www.lagou.com',
                'Referer':            'https://www.lagou.com/jobs/list_python?city=%E5%85%A8%E5%9B%BD',
                'User-Agent':         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                'X-Anit-Forge-Code':  '0',
                'X-Anit-Forge-Token': 'None',
                'X-Requested-With':   'XMLHttpRequest'
            }
            data = {
                'first': True,
                'pn':    page,
                'kd':    keys,
            }
            url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
            print(url)
            resp = requests.post(url, headers=headers1, data=data)
            if resp.status_code == 200:
                print("200")
                parse_content(resp.json())
            return None
        return None
    except ConnectionError as e:
        print("Error", e.args)

def parse_content(json):
    if json:
        print('开始解析数据......')
        results = json.get('content').get('positionResult').get('result')
        for result in results:
            lagou = {}
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
            save_to_json(lagou)

def save_to_json(result):
    if result['city'] not in "":
        print('准备保存数据......')
        with open('data.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(result, indent=2, ensure_ascii=False))
            f.close()
            print('保存成功......')

def save_to_csv(result):
    if result['city'] not in "":
        print('准备保存数据......')
        with open('data.csv', 'a') as f:
            fieldnames = [
                'city', 'businessZones', 'companyFullName', 'companyLabelList', 'companyLogo', 'companyShortName',
                'companySize', 'createTime', 'district', 'education', 'financeStage', 'firstType', 'hitags',
                'industryField', 'jobNature', 'linestaion', 'positionAdvantage', 'positionLables', 'positionName',
                'salary', 'secondType', 'stationname', 'subwayline', 'workYear']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(result)
            f.close()
            print('保存成功-------')

def main():
    start = time.time()
    keys = input("输入要查询的职位: ")
    for i in range(1, 31):
        get_index_ajax(keys, i)
    end = time.time()
    print('程序共耗时: ', end - start)

if __name__ == '__main__':
    main()