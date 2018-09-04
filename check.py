#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 检查解析规则是否失效 '''


def parse_checker(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    job_name = soup.select_one(".job-name .name").string
    assert bool(job_name) is True, 'job_name解析规则发生了变化'

    depart_name = soup.select_one(".company").string
    assert bool(depart_name) is True, 'depart_name解析规则发生了变化'

    city = soup.select(".job_request span")[1].string.strip('/').strip()
    assert bool(city) is True, '%s解析规则发生了变化' % city

    experience = soup.select(".job_request span")[2].string.strip('/').strip()
    assert bool(experience) is True, '%s解析规则发生了变化' % experience

    edu = soup.select(".job_request span")[3].string.strip('/').strip()
    assert bool(edu) is True, '%s解析规则发生了变化' % edu

    work_time = soup.select(".job_request span")[4].string.strip('/').strip()
    assert bool(work_time) is True, '%s解析规则发生了变化' % work_time

    advantage = soup.select_one(".job-advantage p").string
    assert bool(advantage) is True, '%s解析规则发生了变化' % advantage

    job_desc = soup.select_one(".job_bt").text
    assert bool(job_desc) is True, '%s解析规则发生了变化' % job_desc

    addr = ''.join(soup.select_one(".work_addr").text.split()[:-1])
    assert bool(addr) is True, '%s解析规则发生了变化' % addr

    company = soup.select_one(".job_company h2").text.split()[0]
    assert bool(company) is True, '%s解析规则发生了变化' % company

    comp_field = soup.select(".c_feature li")[0].text.split()
    assert bool(comp_field) is True, '%s解析规则发生了变化' % comp_field

    progress = soup.select(".c_feature li")[1].text.split()[0]
    assert bool(progress) is True, '%s解析规则发生了变化' % progress

    scale = soup.select(".c_feature li")[2].text.split()[0]
    assert bool(scale) is True, '%s解析规则发生了变化' % scale

    comp_url = soup.select(".c_feature li")[3].text.split()[0]
    assert bool(comp_url) is True, '%s解析规则发生了变化' % comp_url
