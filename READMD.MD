## 拉勾爬虫

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



可见只需要一个循环遍历所有页，带上pn和kd参数即可，抓包的时候记得关Charles





