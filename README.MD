# 拉勾爬虫

爬取成都地区的Python工作职位





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



## 开启多线程爬取

#### 方法1： 

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



#### 方法2

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