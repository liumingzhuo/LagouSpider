# 拉勾爬虫



- ### 成都版

  爬取成都地区的Python工作职位

- ### 全国版

  抓取整站数据





# 成都Python版



## 网页结构分析

1. 分页式
2. 网页源代码里没有信息，是Ajax加载的



## Charles抓包分析

#### ajax url：

https://www.lagou.com/jobs/positionAjax.json?city=%E6%88%90%E9%83%BD&needAddtionalResult=false

#### Form Data:

first:  true       是否是首页

pn:	1		页数

kd: Python	搜索的关键字



可见只需要一个循环遍历所有页，带上pn和kd参数即可，爬取的时候记得关Charles



#### 开启多线程爬取

```python
threads = []
for i in range(1, pages + 1):
    t = threading.Thread(target=main, args=(keyword, i))
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()
```

```python
for i in range(1, pages + 1):
    t = threading.Thread(target=main, args=(keyword, i))
    t.start()
t.join()
```





## 拉勾的反爬措施和解决

1. 无法直接访问ajax url

   > 带上Referer

2. 短时间访问过多

   > 换 cookie 

3. 多线程一开启就卡住，很久才完成

   > 使用pycharm的cprofile工具进行分析，发现96.6%的时间花在了<method 'acquire' of _thread.lock objects> 上,  喵？

4. 被限制IP频率,一个IP一分钟内只能连续请求5次，多了就封

   > 把频率降到一分钟5次以下, sleep(15) 即可以正常抓取了

5. 为什么浏览器正常访问就可以超过5次呢？

   > 喵？

6. 正常访问和换代理和降速度也不行了，换IP也不行了？

   > 策略没有问题，是代理IP可用性差，再换一个

7. 多线程和延迟矛盾

   > 多取一些IP，每个线程分别取代理IP，反正保证每个IP使用频率不超过警戒线



按照上述的策略就可以顺利的爬取拉勾网的数据了，为了提高速度，多弄点IP吧





# 整站版



## 思路

#### 主思路：从首页出发，递归抓取所有带lagou字符串的新url，放入待爬队列

#### 具体步骤：

1. 将start_url放入待爬队列
2. 调用通用信息爬虫函数，抓取所有带lagou字符串的新url，放入待爬队列
3. 从待爬队列取url，将url进行正则匹配
4. 如果匹配到职位正则，调用职位爬取函数，并将此url放入已爬队列
5. 如果匹配到公司正则，调用公司爬取函数，并将此url放入已爬队列
6. 如果两者均不是，调用通用信息爬虫函数，返回步骤1，继续爬取

爬虫终止条件：爬完所有待爬队列里的url



## 使用Redis进行去重和保存url队列

通过Redis的集合进行去重，同时避免了爬虫出现异常状况又重头开始



## 拆分函数

将各个功能拆分开来，使爬虫结构清晰，同时出了问题便于定位和调试

每个函数只做一件事，也方便进行单元测试

