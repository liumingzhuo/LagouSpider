![logo](https://github.com/huangke19/LagouSpider/raw/master/lines/logo.jpg)


# LagouSpdier

> "What I cannot create, I do not understand."
>
> -- Richard Feynman

本仓库包含两个爬虫

- [小爬虫](https://github.com/huangke19/LagouSpider/blob/master/lagou_index.py)只爬取成都地区的工作职位，可以指定职位名字和要爬的页数
- [大爬虫](https://github.com/huangke19/LagouSpider/blob/master/lagou_whole_site.py)是爬取拉勾整站的爬虫，分为[单机版](https://github.com/huangke19/LagouSpider/blob/master/lagou_whole_site.py)和分布式版([master](https://github.com/huangke19/LagouSpider/blob/master/lagou_master.py)/[slave](https://github.com/huangke19/LagouSpider/blob/master/lagou_slave.py))



准备工作

第一步，观察一下拉勾网的robots.txt，看一下有没有什么可用的信息

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

- ###### ajax url：

  > https://www.lagou.com/jobs/positionAjax.json?city=%E6%88%90%E9%83%BD&needAddtionalResult=false
  >
  > url解码后 https://www.lagou.com/jobs/positionAjax.json?city=成都&needAddtionalResult=false

- ###### Form Data:

  > | first |  true  |  是否是首页  |
  > | :---: | :----: | :----------: |
  > |  pn   |   1    |     页数     |
  > |  kd   | Python | 搜索的关键字 |




可见只需要一个循环遍历所有页，带上pn和kd参数即可，爬取的时候记得关Charles



![line](https://github.com/huangke19/LagouSpider/raw/master/lines/bird.jpg)

## 整站爬虫



#### 思路

> 主思路：从首页出发，递归抓取所有带lagou字符串的新url，放入待爬队列
>

![workflow](https://github.com/huangke19/LagouSpider/raw/master/lines/workflow.jpg)

#### 具体步骤

1. 将start_url放入待爬队列
2. 调用通用信息爬虫函数，抓取所有带lagou字符串的新url，放入待爬队列
3. 从待爬队列取url，将url进行正则匹配
4. 如果匹配到职位正则，调用职位爬取函数，并将此url放入已爬队列
5. 如果匹配到公司正则，调用公司爬取函数，并将此url放入已爬队列
6. 如果两者均不是，调用通用信息爬虫函数，并将此url放入已爬队列
7. 返回步骤3，继续爬取

> 爬虫终止条件：爬完所有待爬队列里的url
>



#### 使用Redis进行去重和保存url队列

> 通过Redis的集合进行去重，同时保存已爬和待爬队列，避免了爬虫出现异常状况又重头开始爬
>



#### 拆分函数

- 将各个功能拆分开来，使爬虫结构清晰，同时出了问题便于定位和调试

- 每个函数只做一件事，也方便进行单元测试




#### 当前爬虫速度

> 每小时爬取10万个页面，其中有效信息（职位信息）一万条
>



![gif](https://github.com/huangke19/LagouSpider/raw/master/lines/gif.gif)



#### 改进爬虫

- 添加重试次数
- 爬取的url分类保存ip





![dd](https://github.com/huangke19/LagouSpider/raw/master/lines/bird.jpg)





## 改造成分布式

- 主从式分布爬虫：使用master节点抓取职位url并入列，使用slave节点取队列中取url进行抓取

- 对等式分布爬虫： 使用上面的全站爬虫分别在不同的机器上运行，设置好共用redis和mongodb即可




#### 开启Redis远程连接

- 配置redis.conf文件，开启远程连接，注释掉bind，将保护模式关闭

  如果/usr/local/etc/下没有redis.conf文件，考虑用brew重装mo

  ```
  # bind 127.0.0.1 
  protected mode no
  ```

- 开启mongodb远程连接

  ```
  bindip: 本机IP，slaveIP
  ```





![dd](https://github.com/huangke19/LagouSpider/raw/master/lines/bird.jpg)



## 拉勾的反爬措施和解决

>|             反爬              |     解决方案     |
>| :---------------------------: | :--------------: |
>|     直接访问ajax url 403      |   带上Referer    |
>| 无Cookie时限制IP频率（5/min） | 带上有效的Cookie |



#### 报443错误

```
TTPSConnectionPool(host='www.lagou.com', port=443): Max retries exceeded with url: /gongsi/j144972.html (Caused by ProxyError('Cannot connect to proxy.', timeout('_ssl.c:817: The handshake operation timed out',)))
```

1. 首先尝试一下回退降速，看一下到底是不是被封IP了
2. 问题解决了，没有被封IP，再提速后恢复正常，是服务器临时出了问题？
3. charles软件引起的





#### 思考的问题

1. 为什么手动点网站可以点很多次，但是用爬虫就被限制到5次第分钟呢？

   > 5次限制：经过试验，发现如果不带Cookie，那就只能每分钟访问5次，带上Cookie后可以突破此限制

2. 每次访问的Cookie有区别吗？

   > 经对比，每一页的Cookie是一样的

3. 部分职位已经过期清空

   > 写一个checker进行判断，如果有“已下线”标志就直接返回不解析

4. 如何应对返回码是200，但是页面并不是我们要的页面（比如是要求填验证码的页面）

   > 在soup解析时进行检查

5. 如何应对解析规则变化？

   > 对解析函数写一个测试，通过assert语句定位具体是哪一条解析错误



按照上述的策略就可以顺利的爬取拉勾网的数据了，为了提高速度，多弄点IP吧



## 结果

当前爬取拉勾整站链接约200万，剩余约70万url待爬取，获取目标职位数据 17万，耗时一夜加一上午，继续爬取中，数据待分类... 
