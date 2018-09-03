# *拉勾爬虫*

![lagou](https://github.com/huangke19/LagouSpider/raw/master/lagou.jpg)

> "What I cannot create, I do not understand."
>
> -- Richard Feynman



本仓库包含两个爬虫，[小爬虫](https://github.com/huangke19/LagouSpider/blob/master/lagou_index_page.py)只爬取成都地区的工作职位，可以指定职位名字和要爬的页数，[大爬虫](https://github.com/huangke19/LagouSpider/blob/master/lagou_whole_site.py)是爬取拉勾整站的爬虫，正在编写中...







![line](https://github.com/huangke19/LagouSpider/raw/master/lines/line.png)

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

|         反爬         |  解决方案   |
| :------------------: | :---------: |
| 直接访问ajax url 403 | 带上Referer |
| 限制IP频率（5/min）  |  降速+切IP  |
|       MaxRetry       | 刷新Cookie  |

按照上述的策略就可以顺利的爬取拉勾网的数据了，为了提高速度，多弄点IP吧







![line](https://github.com/huangke19/LagouSpider/raw/master/lines/line.png)

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

