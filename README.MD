# *拉勾爬虫*

> "What I cannot create, I do not understand."
>
> -- Richard Feynman



本仓库包含两个爬虫，[小爬虫](https://github.com/huangke19/LagouSpider/blob/master/lagou_index.py)只爬取成都地区的工作职位，可以指定职位名字和要爬的页数，[大爬虫](https://github.com/huangke19/LagouSpider/blob/master/lagou_whole_site.py)是爬取拉勾整站的爬虫，正在编写中...

![line](https://github.com/huangke19/LagouSpider/raw/master/lines/bird.jpg)



第一步，观察一下拉勾网的robots.txt，看一下有没有什么可用的信息

```python
https://www.lagou.com/robots.txt

User-agent: Jobuispider
Disallow:  /

User-agent: *
Disallow: /resume/
Disallow: /nearBy/
Disallow: /ologin/
Disallow: /jobs/list_*
Disallow: /one.lagou.com
Disallow: /ns3.lagou.com
Disallow: /hr.lagou.com
Disallow: /two.lagou.com
Disallow: /t/temp1/
Disallow: /center/preview.html
Disallow: /center/previewApp.html
Disallow: /*?utm_source=*
Allow: /gongsi/interviewExperiences.html?companyId=*
Disallow: /*?*
```

这… 基本就没有什么是允许的了，只有disobey了



第二步，查看的拉勾的sitemap，没找到

第三步，估算拉勾的总大小，大约68万条数据

> 使用谷歌高级搜索查询 site:www.lagou.com
>
> 找到约 682,000 条结果 （用时 0.14 秒） 



![dd](https://github.com/huangke19/LagouSpider/raw/master/lines/bird.jpg)



## 小爬虫


#### 网页结构分析

- 翻页式
- 信息是Ajax加载的



#### Charles抓包分析

#### ajax url：

- https://www.lagou.com/jobs/positionAjax.json?city=%E6%88%90%E9%83%BD&needAddtionalResult=false


#### Form Data:

- first:  true       是否是首页

- pn:	1		页数

- kd: Python	搜索的关键字


可见只需要一个循环遍历所有页，带上pn和kd参数即可，爬取的时候记得关Charles



#### 拉勾的反爬措施和解决

|             反爬              |     解决方案     |
| :---------------------------: | :--------------: |
|     直接访问ajax url 403      |   带上Referer    |
| 无Cookie时限制IP频率（5/min） | 带上有效的Cookie |

一更：开了30个线程爬了一个小时，终于激活了拉勾的新反爬措施，现在报443错误了，等的就是你！

```
TTPSConnectionPool(host='www.lagou.com', port=443): Max retries exceeded with url: /gongsi/j144972.html (Caused by ProxyError('Cannot connect to proxy.', timeout('_ssl.c:817: The handshake operation timed out',)))
```

开始解决问题

1. 首先尝试一下回退降速，看一下到底是不是被封IP了

按照上述的策略就可以顺利的爬取拉勾网的数据了，为了提高速度，多弄点IP吧



#### 问题

1. 为什么手动点网站可以点很多次，但是用爬虫就被限制到5次第分钟呢？

   > 5次限制：经过试验，发现如果不带Cookie，那就只能每分钟访问5次，带上Cookie后可以突破此限制

2. 每次访问的Cookie有区别吗？

   > 经对比，每一页的Cookie是一样的





![line](https://github.com/huangke19/LagouSpider/raw/master/lines/bird.jpg)

## 整站爬虫



#### 思路

主思路：从首页出发，递归抓取所有带lagou字符串的新url，放入待爬队列

![workflow](https://github.com/huangke19/LagouSpider/raw/master/workflow.jpg)

#### 具体步骤：

> 1. 将start_url放入待爬队列
> 2. 调用通用信息爬虫函数，抓取所有带lagou字符串的新url，放入待爬队列
> 3. 从待爬队列取url，将url进行正则匹配
> 4. 如果匹配到职位正则，调用职位爬取函数，并将此url放入已爬队列
> 5. 如果匹配到公司正则，调用公司爬取函数，并将此url放入已爬队列
> 6. 如果两者均不是，调用通用信息爬虫函数，并将此url放入已爬队列
> 7. 返回步骤3，继续爬取
>

爬虫终止条件：爬完所有待爬队列里的url



#### 使用Redis进行去重和保存url队列

通过Redis的集合进行去重，同时保存已爬和待爬队列，避免了爬虫出现异常状况又重头开始爬



#### 拆分函数

将各个功能拆分开来，使爬虫结构清晰，同时出了问题便于定位和调试

每个函数只做一件事，也方便进行单元测试



![gif](https://github.com/huangke19/LagouSpider/raw/master/gif.gif)

