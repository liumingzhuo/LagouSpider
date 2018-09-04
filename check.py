#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 检查解析规则是否失效 '''


def parse_checker(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    try:
        online = soup.select_one(".outline_tag").string
        if online == '（该职位已下线）':
            print('该职位已下线')
            return
    except AttributeError:
        pass

    assert soup.select_one(".job-name .name").string, 'job_name解析规则发生了变化'
    assert soup.select_one(".company").string, 'depart_name解析规则发生了变化'
    assert soup.select(".job_request span")[1].string.strip('/').strip(), 'city解析规则发生了变化'
    assert soup.select(".job_request span")[2].string.strip('/').strip(), 'experience解析规则发生了变化'
    assert soup.select(".job_request span")[3].string.strip('/').strip(), 'edu解析规则发生了变化'
    assert soup.select(".job_request span")[4].string.strip('/').strip(), 'work_time解析规则发生了变化'
    assert soup.select_one(".job-advantage p").string, 'advantage 解析规则发生了变化'
    assert soup.select_one(".job_bt").text, 'job_desc解析规则发生了变化'
    assert ''.join(soup.select_one(".work_addr").text.split()[:-1]), 'addr解析规则发生了变化'
    assert soup.select_one(".job_company h2").text.split()[0], 'company解析规则发生了变化'
    assert soup.select(".c_feature li")[0].text.split(), 'comp_field解析规则发生了变化'
    assert soup.select(".c_feature li")[1].text.split()[0], 'progress解析规则发生了变化'
    assert soup.select(".c_feature li")[2].text.split()[0], 'scale解析规则发生了变化'
    assert soup.select(".c_feature li")[3].text.split()[0], ' comp_url解析规则发生了变化'


def anspider_checker(html):
    pass
